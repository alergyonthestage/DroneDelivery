from socket import socket, AF_INET, SOCK_DGRAM
from message import Message, AVAILABLE, BUSY, UNAVAILABLE, DELIVER
from droneDictionary import DroneDictionary
from queue import Queue
from threading import Thread
import time

SOCKET_TIMEOUT_SEC = 2

class SocketOperator(Thread):    
    communicate = True
    
    def __init__(self, udpSocket, recivedMsgsQueue, toSendQueue):
        super().__init__()
        self.udpSocket = udpSocket
        self.recivedMsgsQueue = recivedMsgsQueue
        self.toSendQueue = toSendQueue
        
    def _sendMsgToDrone(self, cmd, data, droneAddress):
        try:
            self.udpSocket.sendto(Message(cmd, data).getBytes(), droneAddress)
            print("Message: [", cmd, " - ", data, "] sent to ", droneAddress)
        except Exception as e:
            print("Cannot send Message: [", cmd, " - ", data, "] to ", droneAddress, ". Exception: ", e)
            
    def _receiveMsgFromDrones(self):
        try:
            print("Waiting to receive a message...")
            data, address = self.udpSocket.recvfrom(2048)
            msg = Message.fromBytes(data)
            return msg.getCmd(), msg.getData(), address
        except TimeoutError:
            raise
        except Exception as e:
            print("Exception!", e)
            
    def run(self):
        while self.communicate:
            startSending = time.time()
            while(not self.toSendQueue.empty() and (time.time()-startSending < SOCKET_TIMEOUT_SEC)):
                self._sendMsgToDrone(*self.toSendQueue.get())
            try:
                self.recivedMsgsQueue.put(self._reciveMsgFromDrones())
            except TimeoutError:
                pass

class DroneMsgsHandler(Thread):
    handleMsgs = True
    
    def __init__(self, recivedMsgsQueue, toSendQueue, droneDictionary):
        self.recivedMsgsQueue = recivedMsgsQueue
        self.toSendQueue = toSendQueue
        self.droneDictionary = droneDictionary
        
    def _availableDrone(self, droneIP, dronePort, droneName):
        if(self.droneDictionary.isDroneUnavailable(droneIP)):
            self.droneDictionary.addAvailableDrone(droneIP, droneName, dronePort)
        else: #if drone was already present in dicrionary
            if(self.droneDictionary.isDroneBusy(droneIP)):
                self.droneDictionary.moveToAvailableDrones(droneIP)
            self.droneDictionary.updateDroneInfos(droneIP, dronePort, droneName)
        self.toSendQueue.put((AVAILABLE, '', (droneIP, dronePort)))
        
    def _unavailableDrone(self, droneIP, dronePort):
        if(self.droneDictionary.isDroneBusy(droneIP)):
            #cannot remove drone since it's busy: NAK = BUSY msg
            self.toSendQueue.put((BUSY, '', (droneIP, dronePort)))
        else:
            if(self.droneDictionary.isDroneAvailable(droneIP)):
                self.droneDictionary.removeUnavailableDrone(droneIP)
            self.toSendQueue.put((UNAVAILABLE, '', (droneIP, dronePort)))
    
    def _busyDrone(self, droneIP, dronePort):
        pass
        #if is for non confirmed delivery (= original msg)
            #confirm delivery to drone
            #confirm delivery to client
        #elif is for already confirmed delivery (= retransmit)
            #confirm delivery to drone
        #else if delivery does not exists 
            #send available msg to drone (NAK = annulla consegna)
    
    def run(self):
        while self.handleMsgs:
            if not self.recivedMsgsQueue.empty():
                cmd, data, addr = self.recivedMsgsQueue.get()
                if(cmd == AVAILABLE):
                    droneName = data
                    self._availableDrone(addr[0], addr[1], droneName)
                elif(cmd == UNAVAILABLE):
                    self._unavailableDrone(addr[0], addr[1])
                elif(cmd == BUSY):
                    pass

class GatewayUDP:
    recivedMsgsQueue = Queue(0)
    toSendQueue = Queue(0)
    
    def __init__(self, serverAddress, serverPort):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind((serverAddress, serverPort))
        self.serverSocket.settimeout(SOCKET_TIMEOUT_SEC)
        self.droneDictionary = DroneDictionary()
        self.socketOperator = SocketOperator(self.serverSocket, self.recivedMsgsQueue, self.toSendQueue)
        self.socketOperator.start()
        self.droneMsgsHandler = DroneMsgsHandler(self.recivedMsgsQueue, self.toSendQueue, self.droneDictionary)
        self.droneMsgsHandler.start()
                
    """    def _waitDeliverAck():
        return 1
            
   def askDeliver(self, shippingAddress, droneIP):
        drone = self.droneDictionary.getAvailableDroneInfos()
        if(drone != None):
            dronePort = (droneIP, drone.get('port'))
            self.sendMsgToDrone(DELIVER, shippingAddress, (droneIP, dronePort))
            print("Waiting drone to accept delivery...")
            
        else:
            print("Drone {} not available!".format(droneIP))"""
 

 

                    
