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
            print("Message: [", cmd, " - ", data, "] sent.")
        except Exception as e:
            print("Exception!", e)
            
    def _receiveMessage(self):
        try:
            msg = Message.fromBytes(self.connectionSocket.recv(2048))
            print("New message recived: ", msg.getCmd(), " - ", msg.getData())
            return msg.getCmd(), msg.getData()
        except Exception as e:
            print("Exception!", e)
            
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
        for drone in dronesList:
            stringList += "DroneIP: " + str(drone[0]) + "\t\t" + str(drone[1]) + "\n"
        return stringList
    
    def _sendDronesList(self):
        if(self.droneDictionary.hasAvailableDrones()):
            self._sendMessage(LIST_DRONES, self.getStringDronesList())
        else:
            self._sendMessage(EXCEPTION, "There's not any available drone.")
        
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
            print("Handshake socket created, all requests will be added to queue.")
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
            raise AnotherClientConnected('The gateway can only handle one client at a time.')
        else:
            print("Waiting for a TCP client request!")
            connectionSocket, address = self.handshakeSocket.accept()
            confirmed = self._confirmClientConnection(address)
            self.clientHandler = ClientHandler(connectionSocket, confirmed, self.deliveriesRegister, self.droneDictionary)
            self.clientHandler.start()
            self.clientHandler.join()
            self.clientHandler = None