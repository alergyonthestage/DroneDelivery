from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import threading

#porta a cui voglio ricevere le richieste e i messaggi client
serverPort = 12000
mantainConnection = True
    
class Gateway:
    def __init__(self, serverAddress, serverPort):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((serverAddress, serverPort))
        self.socket.listen(1)
        
    def handleClient(self, connectionSocket):
        while mantainConnection:
            message = connectionSocket.recv();

    def acceptClient(self):
        print("waiting for a Client")
        connectionSocket, address = self.socket.accept()
        if confirmClientConnection(address):
            print("Connection Accepted")
            threading.Thread(target=self.handleClient, args=connectionSocket)
        else:
            print("Connection Denied!")
            connectionSocket.close()

def handleClient(clientSocket, clientAddress):
    global mantainConnection
    while mantainConnection:
        message = clientSocket.recv(2048).decode()
        if (message == "closeConn"):
            mantainConnection = False
        reply = message.upper()
        clientSocket.send(reply.encode()) 

while True:
    print("waiting for a Client")
    connectionSocket, address = serverSocket.accept()
    if confirmClientConnection(address):
        print("Connection Accepted")
        handleClient(connectionSocket, address)
        mantainConnection = True
    connectionSocket.close()
    print("Connection Closed")