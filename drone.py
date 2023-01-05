from socket import socket, AF_INET, SOCK_DGRAM
from message import Message, AVAILABLE, BUSY, DELIVER

class Drone:
    
    def __init__(self, gatewayIP = '', gatewayPort = '', droneID = 0):
        self.gatewayAddress = (gatewayIP, gatewayPort)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.id = droneID
        self.status = AVAILABLE
        
    def sendToGateway(self, message):
        self.socket.sendto(message.encode(), self.gatewayAddress)
        
