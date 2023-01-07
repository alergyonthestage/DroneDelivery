from socket import socket, AF_INET, SOCK_STREAM
from message import Message, START_CONN, CLOSE_CONN, EXCEPTION, LIST_DRONES, DELIVER
from threading import Thread

#handshake port
handshakePort = 12000

class ClientHandler(Thread):
    mantainConnection = True
    
    def __init__(self, connectionSocket, clientAccepted, deliveriesRegister, droneDictionary):
        super().__init__()
        if(clientAccepted): 
            self.connectionSocket = connectionSocket
            self._sendMessage(START_CONN, '')
            print("Connection Accepted")
            self.deliveriesRegister = deliveriesRegister
            self.droneDictionary = droneDictionary
        else:
            self._sendMessage(CLOSE_CONN, '')
            print("Connection Denied!")
            connectionSocket.close()
    
    def _sendMessage(self, cmd, data):
        try:
            msgBytes = Message(cmd, data).getBytes()
            self.connectionSocket.send(msgBytes)
            print("\nMessage: [", cmd, " - ", data, "] sent from gateway (", self.connectionSocket.getsockname() ,") to client (", self.connectionSocket.getpeername(), ")\n")
        except Exception as e:
            print("Cannot send message to gateway. Exception:", e)
            
    def _receiveMessage(self):
        try:
            msg = Message.fromBytes(self.connectionSocket.recv(2048))
            print("\nMessage [", msg.getCmd(), " - ", msg.getData(), "] recived from client (", self.connectionSocket.getpeername(), ") to gateway (", self.connectionSocket.getsockname(), "\n")
            return msg.getCmd(), msg.getData()
        except Exception as e:
            print("Cannot receive Messages from client. Exception:", e)
            
    def _canDisconnectClient(self):
        return True
            
    def _disconnectClient(self):
        print("Try to disconnect client: ", self.connectionSocket.getpeername())
        if (self._canDisconnectClient()):
            self._sendMessage(CLOSE_CONN, '')
            self.mantainConnection = False
            self.connectionSocket.close()
        else:
            self._sendMessage(EXCEPTION, 'Cannot disconnect client!')
   
    def getStringDronesList(self):
        stringList = ""
        dronesList = self.droneDictionary.getAvailableDrones()
        n = 1
        for drone in dronesList:
            port = str(drone[1].get('port'))
            name = str(drone[1].get('name'))
            addTime = str(drone[1].get('addTime'))
            stringList += "N." + str(n) + "\t" + "DroneIP: " + str(drone[0]) + "\t\tPort: " + port + "\tName: " + name + "\tAvailable since: " + addTime +"\n"
            n += 1
        return stringList
    
    def _sendDronesList(self):
        if(self.droneDictionary.hasAvailableDrones()):
            self._sendMessage(LIST_DRONES, self.getStringDronesList())
        else:
            self._sendMessage(EXCEPTION, "No available drones found! Retry later...")
        
    def _deliver(self, msgData):
        droneIP, shippingAdderss = msgData.split("_")
        self.deliveriesRegister.requestDelivery(droneIP, shippingAdderss)
        
    def run(self):
        while self.mantainConnection:
            msgCmd, msgData = self._receiveMessage()
            if(msgCmd == CLOSE_CONN):
                self._disconnectClient()
            elif(msgCmd == LIST_DRONES):
                self._sendDronesList()
            elif(msgCmd == DELIVER):
                self._deliver(msgData)

class AnotherClientConnected(Exception):
    pass

class ClientSideGateway:
    clientHandler = None
    
    def __init__(self, serverAddress, serverPort, deliveriesRegister, droneDictionary):
        self.deliveriesRegister = deliveriesRegister
        self.droneDictionary = droneDictionary
        try:
            self.handshakeSocket = socket(AF_INET, SOCK_STREAM)
            self.handshakeSocket.bind((serverAddress, serverPort))
            self.handshakeSocket.listen(1)
            print("TCP Handshake socket created.")
        except Exception as e:
            print("Exception!", e) 
            
    def _confirmClientConnection(self, address):
        print("Il client {} sta richiedendo la connessione.".format(address))
        choice = input("Accettare la connessione? [Y/N] ")
        if choice.lower() == "y":
            return True
        else:
            return False

    def handleClient(self):
        if(self.clientHandler != None):
            raise AnotherClientConnected('Another client is already connected. The gateway can only handle one client at a time.')
        else:
            print("Waiting for a client request!")
            connectionSocket, address = self.handshakeSocket.accept()
            confirmed = self._confirmClientConnection(address)
            self.clientHandler = ClientHandler(connectionSocket, confirmed, self.deliveriesRegister, self.droneDictionary)
            self.clientHandler.start()
            self.clientHandler.join()
            self.clientHandler = None