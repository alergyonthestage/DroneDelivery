from socket import socket, AF_INET, SOCK_STREAM
from message import Message, START_CONN, CLOSE_CONN, EXCEPTION, LIST_DRONES
import threading

#handshake port
handshakePort = 12000

class GatewayTCP:
    mantainConnection = True
    
    def __init__(self, serverAddress, serverPort):
        try:
           self.handshakeSocket = socket(AF_INET, SOCK_STREAM)
           self.handshakeSocket.bind((serverAddress, serverPort))
           self.handshakeSocket.listen(1)
           print("Socket created, all requests will be added to queue. Call acceptClient() method!")
        except Exception as e:
            print("Exception!", e)
            
    def _sendMessage(self, cmd, data, connSocket):
        try:
            msgBytes = Message(cmd, data).getBytes()
            connSocket.send(msgBytes)
            print("Message: [", cmd, " - ", data, "] sent.")
        except Exception as e:
            print("Exception!", e)
            
    def _receiveMessage(self, connSocket):
        try:
            msg = Message.fromBytes(connSocket.recv(2048))
            print("New message recived!")
            return msg.getCmd(), msg.getData()
        except Exception as e:
            print("Exception!", e)
            
    def _canDisconnectClient(self, connectionSocket):
        return True
            
    def _disconnectClient(self, connectionSocket):
        print("Try to disconnect client: ", connectionSocket.getpeername())
        if (self._canDisconnectClient(connectionSocket)):
            self._sendMessage(CLOSE_CONN, '', connectionSocket)
            connectionSocket.close()
            self.mantainConnection = False
        else:
            self._sendMessage(EXCEPTION, 'Cannot disconnect client!', connectionSocket)
   
    def _sendDronesList(self, socket):
        #se ci sono droni connessi invia, altrimenti exception
        self._sendMessage(LIST_DRONES, '1,2,3,4,5,6', socket)
        
    def _handleClient(self, connectionSocket):
        while self.mantainConnection:
            msgCmd, msgData = self._receiveMessage(connectionSocket)
            print(msgCmd, " - ", msgData)
            if (msgCmd == CLOSE_CONN):
                self._disconnectClient(connectionSocket)
            elif (msgCmd == LIST_DRONES):
                self._sendDronesList(connectionSocket)
        self.mantainConnection = True
            
    def _confirmClientConnection(self, address):
        print("Il client {} sta richiedendo la connessione.".format(address))
        choice = input("Accettare la connessione? [Y/N] ")
        if choice.lower() == "y":
            return True
        else:
            return False
        
    def acceptClient(self):
        print("Waiting for a TCP client request!")
        connectionSocket, address = self.handshakeSocket.accept()
        if self._confirmClientConnection(address):
            self._sendMessage(START_CONN, '', connectionSocket)
            print("Connection Accepted")
            newThread = threading.Thread(target = self._handleClient, args = (connectionSocket, ))
            newThread.start()
        else:
            self._sendMessage(CLOSE_CONN, '', connectionSocket)
            print("Connection Denied!")
            connectionSocket.close()

gateway = GatewayTCP('', handshakePort)
gateway.acceptClient()
gateway.handshakeSocket.close()
