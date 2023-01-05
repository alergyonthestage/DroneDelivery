from socket import socket, AF_INET, SOCK_DGRAM
from message import Message, AVAILABLE, BUSY, DELIVER
from droneDictionary import DroneDictionary
from queue import Queue
from threading import Thread
import time

SOCKET_TIMEOUT_SEC = 2

class GatewayUDP:
    recivedMsgs = Queue(0)
    toSendMsgs = Queue(0)
    communicate = True
    handleMsg = True
    
    def __init__(self, serverAddress, serverPort):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind((serverAddress, serverPort))
        self.serverSocket.settimeout(SOCKET_TIMEOUT_SEC)
        self.droneDictionary = DroneDictionary()
        self.droneMsgCollector = threading.Thread(target = self._communicateWithDrones)
        
    def _sendMsgToDrone(self, cmd, data, droneAddress):
        try:
            self.serverSocket.sendto(Message(cmd, data).getBytes(), droneAddress)
            print("Message: [", cmd, " - ", data, "] sent to ", droneAddress)
        except Exception as e:
            print("Cannot send Message: [", cmd, " - ", data, "] to ", droneAddress, ". Exception: ", e)
            
    def _receiveMsgFromDrones(self):
        try:
            print("Waiting to receive a message...")
            data, address = self.serverSocket.recvfrom(2048)
            msg = Message.fromBytes(data)
            return msg.getCmd(), msg.getData(), address
        except TimeoutError:
            raise
        except Exception as e:
            print("Exception!", e)
    
    def _communicateWithDrones(self):
        while self.communicate:
            startSending = time.time()
            while(not self.toSendMsgs.empty() or (time.time()-startSending < SOCKET_TIMEOUT_SEC)):
                self._sendMsgToDrone(*self.toSendMsgs.get())
            try:
                self.recivedMsgs.put(self._reciveMsgFromDrones())
            except TimeoutError:
                pass
                   
    def _waitDeliverAck():
        return 1
            
    def askDeliver(self, shippingAddress, droneIP):
        drone = self.droneDictionary.getAvailableDroneInfos()
        if(drone != None):
            dronePort = (droneIP, drone.get('port'))
            self.sendMsgToDrone(DELIVER, shippingAddress, (droneIP, dronePort))
            print("Waiting drone to accept delivery...")
            
        else:
            print("Drone {} not available!".format(droneIP))
 
    def availableDrone(self, droneIP, dronePort, droneName):
        if(self.droneDictionary.getBusyDroneInfos(droneIP) == None):
            if(self.droneDictionary.getAvailableDroneInfos(droneIP) == None):
                DroneDictionary().addAvailableDrone(droneIP, droneName, dronePort)
                #send ACK
        else:
            DroneDictionary().moveToAvailableDrones(droneIP)
            #send ACK
 
    def _handleDroneMessages(self):
        while self.handleMsg:
            if not self.recivedMsgs.empty():
                cmd, data, addr = self.recivedMsgs.get()
                if(cmd == AVAILABLE):
                    
                
            
gateUDP = GatewayUDP('', 12000)
