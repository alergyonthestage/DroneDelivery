from socket import socket, AF_INET, SOCK_DGRAM

BUSY = 0
AVAILABLE = 1

class Drone:
    
    def __init__(self, gatewayIP = '', gatewayPort = '', droneID = 0):
        self.gatewayAddress = (gatewayIP, gatewayPort)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.id = droneID
        self.status = AVAILABLE
        
    def sendToGateway(self, message):
        self.socket.sendto(message.encode(), self.gatewayAddress)
        
