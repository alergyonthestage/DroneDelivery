from socket import socket, AF_INET, SOCK_DGRAM, SOCK_RAW, IPPROTO_RAW, IPPROTO_IP, IP_HDRINCL, timeout, inet_aton
from message import Message, AVAILABLE, BUSY, DELIVER, UNAVAILABLE
#from threading import Thread
import time
import random

DEBUG = False

class NotConnectedToGateway(Exception):
    pass

class AlreadyConnectedToGateway(Exception):
    pass

class Drone:
    RETRANSMIT_TIMEOUT_SEC = 6
    RETRANSMIT_MAX_ATTEMPTS = 3
    gatewayAddress = None
    
    def __init__(self, droneName = 'Unknown'):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(self.RETRANSMIT_TIMEOUT_SEC)
        self.name = droneName
        self.status = UNAVAILABLE
    
    @classmethod 
    def withFakeIp(cls, fakeIP, droneName = 'Unknown'):
        s = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)
        ip_header = b"\x45\x00\x00\x54\x00\x00\x40\x00\x40\x11\x00\x00" + inet_aton(fakeIP) + b"\x7f\x00\x00\x01"
        drone = cls(droneName)
        drone.socket = s
        drone.header = ip_header
        drone.fakeIP = fakeIP
        return drone
        
    def isConnected(self):
        return self.gatewayAddress != None
    
    def _maxAttemptsReached(self, currentAttempts):
        return currentAttempts > self.RETRANSMIT_MAX_ATTEMPTS
        
    def _sendMessage(self, cmd, data):
        if(DEBUG):
            print("DEBUG - Sending MSG to gateway...")
        if(not self.isConnected()):
            raise NotConnectedToGateway('Cannot send a message because the drone is not connected to a Gateway.')
        try:
            msgBytes = Message(cmd, data).getBytes()
            if(hasattr(self, "fakeIP")):
                self.socket.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
                pcktData = self.header + msgBytes
                self.socket.sendto(pcktData, self.gatewayAddress)
            else:
                self.socket.sendto(msgBytes, self.gatewayAddress)
            if(DEBUG):
                print("DEBUG - MSG: '", cmd, " - ", data, "' sent to gateway")
        except Exception as e:
            print("Cannot send Message: [", cmd, " - ", data, "]. Exception: ", e)

    def _receiveMessage(self):
        if(DEBUG):
            print("DEBUG - Reciving MSG from gateway...")
        try:
            msgBytes, addr = self.socket.recvfrom(2048)
            msg = Message.fromBytes(msgBytes)
            if(DEBUG):
                print("DEBUG - MSG: '", msg.getCmd(), " - ", msg.getData(), "' recived from gateway")
            return msg.getCmd(), msg.getData()
        except timeout:
            raise timeout
        except Exception as e:
            print("Cannot recive Messages. Exception: ", e)
            
    def _deliver(self):
        deliveryTime = 10*random.random()
        print("Delivery will take {:.1f} seconds.\n".format(deliveryTime))
        time.sleep(deliveryTime)
        print("DELIVERED!\n")
        self._available()
            
    def _waitForDelivery(self):
        replyCmd = None
        print("Waiting for deliveries...\n")
        while(replyCmd != DELIVER):
            try:
                replyCmd, replyData = self._receiveMessage()
            except timeout:
                pass
        self._sendMessage(BUSY, '')
        print("Delivery request recived. Shipping address: ", replyData)
        print("Accepted! Waiting for the gateway to confirm...\n")
        attempts = 1
        replyCmd = None
        while(replyCmd != BUSY and not self._maxAttemptsReached(attempts)):  
            try:
                replyCmd, replyData = self._receiveMessage()
            except timeout: 
                self._sendMessage(BUSY, '')
                attempts += 1
        if(self._maxAttemptsReached(attempts)):
            print("Cannot communicate with gateway. Please, try restarting the drone app!")
            return
        print("Confirm recived! Going to deliver... Now I'm BUSY")
        self.status = BUSY
        self._deliver()
    
    def _available(self):
        self._sendMessage(AVAILABLE, self.name)
        replyCmd = None
        attempts = 1
        while(replyCmd != AVAILABLE and not self._maxAttemptsReached(attempts)):
            try:
                replyCmd, replyData = self._receiveMessage()
            except timeout:
                self._sendMessage(AVAILABLE, self.name)
                attempts += 1
        if(self._maxAttemptsReached(attempts)):
            print("Cannot communicate with gateway. Please, try restarting the drone app!")
            return
        self.status = AVAILABLE
        print("Status: AVAILABLE")
        self._waitForDelivery()
            
    def connectToGateway(self, gatewayIP, gatewayPort):
        print("Connecting to gateway...")
        if(self.isConnected()):
            raise AlreadyConnectedToGateway('The drone is already connected. Disconnect first in order to change gateway.')
        self.gatewayAddress = (gatewayIP, gatewayPort)
        print("Succesfully connected to gateway. Gateway IP: ", gatewayIP, "; Gateway Port: ", gatewayPort)
        print("Making drone available to gateway... \n\n")
        self._available()
        
    def disconnectFromGateway(self):
        if(not self.isConnected()):
            raise NotConnectedToGateway('Unable to disconnect the drone since is not connected to any gateway.')
        if(self.status == BUSY):
            print("Cannot disconnect from gateway. Now I'm BUSY")
            return
        self._sendMessage(UNAVAILABLE, '')
        attempts = 1
        replyCmd = None
        while((replyCmd != UNAVAILABLE or replyCmd != BUSY) and not self._maxAttemptsReached(attempts)):
            try:
                replyCmd, replyData = self._receiveMessage()
            except timeout:
                self._sendMessage(UNAVAILABLE, '')
                attempts += 1
        if(self._maxAttemptsReached(attempts)):
            print("Cannot communicate with gateway. Please, try restarting the drone app!")
            return
        if(replyCmd == BUSY):
            print("Something get wrong: i'm BUSY for the gateway, but in realty i'm Available. \nCannot disconnect now, retry later...")
            return
        self.gatewayAddress = None
        self.status = UNAVAILABLE
        print("Disconnected from gateway!")

gatewayIP = ''
gatewayPort = 50000
    

def connectFakeDrone(fakeIP, droneName = 'Unknown'):
    drone = Drone.withFakeIp(fakeIP, droneName)
    drone.connectToGateway(gatewayIP, gatewayPort)

#th1 = Thread(target = connectFakeDrone, args = ('1.2.3.1', 'Fake01'))
#th1.start()
#th2 = Thread(target = connectFakeDrone, args = ('1.2.3.2', 'Fake02'))
#th2.start()
drone = Drone("Alessandro's Drone")
drone.connectToGateway('', 50000)
    