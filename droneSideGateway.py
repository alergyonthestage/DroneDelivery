from socket import socket, AF_INET, SOCK_DGRAM, timeout
from message import Message, AVAILABLE, BUSY, UNAVAILABLE, DELIVER
from droneDictionary import DroneDictionary
from queue import Queue
from threading import Thread
import time

SOCKET_timeoutTime_SEC = 2
RETRANSMIT_TIMEOUT_SEC = 4

class RetransmitTimer(Thread):
    stopped = False
    
    def __init__(self, msgToQueue, timeoutTime, toSendQueue):
        super().__init__()
        self.msgToQueue = msgToQueue
        self.timeoutTime = timeoutTime
        self.toSendQueue = toSendQueue
        
    def stop(self):
        self.stopped = True
    
    def run(self):
        self.startSending = time.time()
        while ((time.time()-self.startSending < self.timeoutTime) and (not self.stopped)):
            pass
        if(not self.stopped):
            self.toSendQueue.put(self.msgToQueue)

class SocketOperator(Thread):    
    communicate = True
    
    def __init__(self, udpSocket, receivedMsgsQueue, toSendQueue, deliverMsgTimers):
        super().__init__()
        self.udpSocket = udpSocket
        self.receivedMsgsQueue = receivedMsgsQueue
        self.toSendQueue = toSendQueue
        self.deliverMsgTimers = deliverMsgTimers
        
    def _sendMsgToDrone(self, cmd, data, droneAddress):
        try:
            self.udpSocket.sendto(Message(cmd, data).getBytes(), droneAddress)
            if(cmd == DELIVER):
                retransmitTimer = RetransmitTimer((cmd, data, droneAddress), RETRANSMIT_TIMEOUT_SEC, self.toSendQueue)
                retransmitTimer.start()
                self.deliverMsgTimers[droneAddress[0]] = retransmitTimer
            print("Message: [", cmd, " - ", data, "] sent to ", droneAddress)
        except Exception as e:
            print("Cannot send Message: [", cmd, " - ", data, "] to ", droneAddress, ". Exception: ", e)
            
    def _receiveMsgFromDrones(self):
        try:
            data, address = self.udpSocket.recvfrom(2048)
            msg = Message.fromBytes(data)
            return msg.getCmd(), msg.getData(), address
        except timeout:
            raise
        except Exception as e:
            print("Exception: ", e)
            
    def run(self):
        while self.communicate:
            startSending = time.time()
            while(not self.toSendQueue.empty() and (time.time()-startSending < SOCKET_timeoutTime_SEC)):
                self._sendMsgToDrone(*self.toSendQueue.get())
            try:
                self.receivedMsgsQueue.put(self._receiveMsgFromDrones())
            except timeout:
                pass

class DroneMsgsHandler(Thread):
    handleMsgs = True
    
    def __init__(self, receivedMsgsQueue, toSendQueue, droneDictionary, deliveriesRegister, deliverMsgTimers):
        super().__init__()
        self.receivedMsgsQueue = receivedMsgsQueue
        self.toSendQueue = toSendQueue
        self.droneDictionary = droneDictionary
        self.deliveriesRegister = deliveriesRegister
        self.deliverMsgTimers = deliverMsgTimers
        
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
        if(self.deliveriesRegister.hasPendingDelivery(droneIP)):
            if(self.deliverMsgTimers.has_Key(droneIP)):
                self.deliverMsgTimers.stop()
                if(self.droneDictionary.isDroneAvailable(droneIP)):
                    self.droneDictionary.moveToBusyDrones(droneIP)
                    self.toSendQueue.put((BUSY, '', (droneIP, dronePort)))
                    self.deliveriesRegister.delivering(droneIP)   
                else:
                    pass
                    #errore connessione persa con il drone non più avviabile
            elif(self.droneDictionary.isDroneBusy(droneIP)):
                #ritrasmetto ACK perso dal drone
                self.toSendQueue.put((BUSY, '', (droneIP, dronePort)))
        else:
            #errore, il drone non doveva consegnare nulla
            self.toSendQueue.put((AVAILABLE, '', (droneIP, dronePort)))
    
    def _requestDelivery(self):
        droneIP, request = self.deliveriesRegister.getNextRequest()
        if(self.droneDictionary.isDroneAvailable(droneIP)):
            dronePort = self.droneDictionary.getAvailableDroneInfos(droneIP)
            self.toSendQueue.put((DELIVER, request.get('shippingAddress'), (droneIP, dronePort)))
        else:
            self.deliveriesRegister.cancelled(droneIP)
    
    def run(self):
        while self.handleMsgs:
            if(not self.receivedMsgsQueue.empty()):
                cmd, data, addr = self.receivedMsgsQueue.get()
                if(cmd == AVAILABLE):
                    droneName = data
                    self._availableDrone(addr[0], addr[1], droneName)
                elif(cmd == UNAVAILABLE):
                    self._unavailableDrone(addr[0], addr[1])
                elif(cmd == BUSY):
                    pass
            if(self.deliveriesRegister.hasNewRequests()):
                self._requestDelivery()

class DroneSideGateway:
    receivedMsgsQueue = Queue(0)
    toSendQueue = Queue(0)
    deliverMsgTimers = {}
    
    def __init__(self, serverAddress, serverPort, deliveriesRegister):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind((serverAddress, serverPort))
        self.serverSocket.settimeout(RETRANSMIT_TIMEOUT_SEC)
        self.droneDictionary = DroneDictionary()
        self.deliveriesRegister = deliveriesRegister
        self.socketOperator = SocketOperator(self.serverSocket, self.receivedMsgsQueue, self.toSendQueue, self.deliverMsgTimers)
        self.socketOperator.start()
        self.droneMsgsHandler = DroneMsgsHandler(self.receivedMsgsQueue, self.toSendQueue, self.droneDictionary, self.deliveriesRegister, self.deliverMsgTimers)
        self.droneMsgsHandler.start()
        
    def getDroneDictionary(self):
        return self.droneDictionary