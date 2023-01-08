from socket import socket, AF_INET, SOCK_DGRAM, timeout
from message import Message, AVAILABLE, BUSY, UNAVAILABLE, DELIVER
from droneDictionary import DroneDictionary
from queue import Queue
from threading import Thread
import time

SOCKET_timeoutTime_SEC = 2
RETRANSMIT_TIMEOUT_SEC = 4
RETRANSMIT_MAX_ATTEMPTS = 3

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
        
    def _attemptsOver(self, droneIP):
        if(self.deliverMsgTimers.get(droneIP) != None):
            return RETRANSMIT_MAX_ATTEMPTS >=(self.deliverMsgTimers.get(droneIP)[1])
        return False
        
    def _scheduleRetransmit(self, cmd, data, droneAddress):
        retransmitTimer = RetransmitTimer((cmd, data, droneAddress), RETRANSMIT_TIMEOUT_SEC, self.toSendQueue)
        retransmitTimer.start()
        if(self.deliverMsgTimers.get(droneAddress[0]) != None):
            attempts = (self.deliverMsgTimers.get(droneAddress[0])[1])+1
        else:
            attempts = 1
        self.deliverMsgTimers[droneAddress[0]] = (retransmitTimer, attempts)
        
    def _sendMsgToDrone(self, cmd, data, droneAddress):
        try:
            self.udpSocket.sendto(Message(cmd, data).getBytes(), droneAddress)
            print("\nMessage [", cmd, " - ", data, "] sent from gateway ", self.udpSocket.getsockname() ," to drone ", droneAddress, "\n")
            if(cmd == DELIVER):
                if(self._attemptsOver(droneAddress[0])):
                    print("Retransmit attempts over. Cannot communicate with drone ", droneAddress, ".")
                else:
                    self._scheduleRetransmit(cmd, data, droneAddress)
        except Exception as e:
            print("Cannot send Message [", cmd, " - ", data, "] to drone ", droneAddress, ". Exception: ", e)
            
    def _receiveMsgFromDrones(self):
        try:
            data, address = self.udpSocket.recvfrom(2048)
            msg = Message.fromBytes(data)
            print("\nMessage [", msg.getCmd(), " - ", msg.getData(), "] recived from drone ", address, " to gateway ", self.udpSocket.getsockname(), ".\n")
            return msg.getCmd(), msg.getData(), address
        except timeout:
            raise
        except Exception as e:
            print("Cannot receive Messages from drones. Exception:", e)
            
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
        if(self.droneDictionary.isDroneUnavailable(droneIP)): #New drone available!
            print("NEW DRONE AVAILABLE! Drone IP: ", droneIP, "Name: ", droneName, "\n")
            self.droneDictionary.addAvailableDrone(droneIP, droneName, dronePort)
        else: #the drone was already present in dicrionary.
            if(self.droneDictionary.isDroneBusy(droneIP)): #the drone was delivering, delivery done!
                deliveryInfos = self.deliveriesRegister.getPendingDeliveryInfos(droneIP)
                print("ORDER DELIVERED! Drone IP: ", droneIP, "Infos: ",deliveryInfos, "\n")
                self.droneDictionary.moveToAvailableDrones(droneIP)
                self.deliveriesRegister.delivered(droneIP)
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
            print("DRONE UNAVAILABLE! Drone IP: ", droneIP, "\n")
    
    def _busyDrone(self, droneIP, dronePort):
        if(self.deliveriesRegister.hasPendingDelivery(droneIP)):
            if(self.deliverMsgTimers.get(droneIP) != None):
                self.deliverMsgTimers.get(droneIP)[0].stop()
                if(self.droneDictionary.isDroneAvailable(droneIP)):
                    self.droneDictionary.moveToBusyDrones(droneIP)
                    self.toSendQueue.put((BUSY, '', (droneIP, dronePort)))
                    self.deliveriesRegister.delivering(droneIP)
                    deliveryInfos = self.deliveriesRegister.getPendingDeliveryInfos(droneIP)
                    print("GOING TO DELIVER! Drone IP: ", droneIP, "Infos: ", deliveryInfos, "\n")
                else:
                    print("Cannot communicate with drone (", droneIP, "). Drone is no longer available\n")
            elif(self.droneDictionary.isDroneBusy(droneIP)): #ritrasmetto ACK perso dal drone
                self.toSendQueue.put((BUSY, '', (droneIP, dronePort)))
        else: #errore, il drone non doveva consegnare nulla
            self.toSendQueue.put((AVAILABLE, '', (droneIP, dronePort)))
    
    def _requestDelivery(self):
        droneIP, request = self.deliveriesRegister.getNextRequest()
        print("DELIVERY REQUESTED to Drone (", droneIP, "). Infos: ", request, "\n")
        if(self.droneDictionary.isDroneAvailable(droneIP)):
            dronePort = self.droneDictionary.getAvailableDroneInfos(droneIP).get('port')
            self.toSendQueue.put((DELIVER, request.get('shippingAddress'), (droneIP, dronePort)))
            print("DELIVERY REQUEST FORWARDED to Drone (", droneIP, ").\n")
        else:
            print("Drone (", droneIP, ") unavailable. Cannot request delivery! Delivery cancelled.")
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
                    self._busyDrone(addr[0], addr[1])
            if(self.deliveriesRegister.hasNewRequests()):
                self._requestDelivery()

class DroneSideGateway:
    receivedMsgsQueue = Queue(0)
    toSendQueue = Queue(0)
    deliverMsgTimers = {}
    
    def __init__(self, serverAddress, serverPort, deliveriesRegister):
        print("Creating drones UDP socket...")
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind((serverAddress, serverPort))
        self.serverSocket.settimeout(RETRANSMIT_TIMEOUT_SEC)
        self.droneDictionary = DroneDictionary()
        self.deliveriesRegister = deliveriesRegister
        self.socketOperator = SocketOperator(self.serverSocket, self.receivedMsgsQueue, self.toSendQueue, self.deliverMsgTimers)
        print("Starting UDP Socket Operator...")
        self.socketOperator.start()
        self.droneMsgsHandler = DroneMsgsHandler(self.receivedMsgsQueue, self.toSendQueue, self.droneDictionary, self.deliveriesRegister, self.deliverMsgTimers)
        print("Starting Drone Messages Handler...")
        self.droneMsgsHandler.start()
        
    def getDroneDictionary(self):
        return self.droneDictionary