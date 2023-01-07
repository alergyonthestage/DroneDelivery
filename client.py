from socket import socket, AF_INET,SOCK_STREAM
from message import Message, START_CONN, CLOSE_CONN, EXCEPTION, LIST_DRONES, DELIVER

class Client:
    def _sendMessage(self, cmd, data):
        try:
            msgBytes = Message(cmd, data).getBytes()
            self.clientSocket.send(msgBytes)
            print("Message: [", cmd, " - ", data, "] sent.")
        except Exception as e:
            print("Cannot send Message: [", cmd, " - ", data, "]. Exception: ", e)
    
    def _receiveMessage(self):
        #TO-DO stampa from/to
        try:
            print("Waiting to receive a message...")
            msgBytes = self.clientSocket.recv(2048)
            print("Message received! Bytes:", msgBytes)
            msg = Message.fromBytes(msgBytes)
            return msg.getCmd(), msg.getData()
        except Exception as e:
            print("Exception!", e)
            
    def _emergencyCloseConnection(self):
        #TO-DO implement try send CLOSE_CONN and then close, else if already disconnected close socket
        self.clientSocket.close()
        
    def connectToGateway(self, serverName, serverPort):
        print("Creating socket and request connection to {} TCP server...".format(serverName))
        try:
            self.clientSocket = socket(AF_INET, SOCK_STREAM)
            self.clientSocket.connect((serverName, serverPort))
        except Exception as e:
            print("Exception!", e)
        print("Waiting the server to confirm the connection...")
        replyCmd, replyData = self._receiveMessage()
        if (replyCmd == START_CONN):
            print("Connected!")
            return True
        elif (replyCmd == CLOSE_CONN):
            self.clientSocket.close()
            print("Connection denied!")
            return False
        else:
            print("Unexpected command recived! The connection will be closed.")
            self._emergencyCloseConnection()
            return False
        
    def closeConnection(self):
        print("Asking the server to close the connection...")
        self._sendMessage(CLOSE_CONN, '')
        replyCmd, replyData = self._receiveMessage()
        if (replyCmd == CLOSE_CONN):
            self.clientSocket.close()
            print("Connection closed!")
            return True
        elif (replyCmd == EXCEPTION):
            print("Failure, connection mantained! Exception: ", replyData)
            return False
        else:
            print("Unexpected command recived!")
            #TO-DO emergency close or emergency recover?
            return False
        
    def getAvailableDrones(self):
        self._sendMessage(LIST_DRONES, '')
        replyCmd, replyData = self._receiveMessage()
        if (replyCmd == LIST_DRONES):
            print(replyData)
        elif (replyCmd == EXCEPTION):
            print("Could not list available Drones! Exception: ", replyData)
            return False
        else:
            print("Unexpected command recived! Packet discarted.")
            return False
        
    def deliver(self, shippingAddress, droneIP):
        msgData = droneIP + "_" + shippingAddress
        self._sendMessage(DELIVER, msgData)      
        
closeConn = False

def printCMDlist():
    print("\n\nCMD numbers: \n" + 
          "0 -> disconnect from gateway and quit client APP \n" +
          "1 -> list available drones \n" +
          "2 -> deliver\n\n")

client = Client()
print("Connecting...")
client.connectToGateway('', 51000)
printCMDlist()
while not closeConn: 
    cmd = input("Insert CMD number: ")
    if(cmd == '0'):
        print("Closing connection with gateway and quit APP")
        client.closeConnection()
        closeConn = True
    elif(cmd == '1'):
        print("Asking for available drones...")
        client.getAvailableDrones()
    elif(cmd == '2'):
        print("New deliver: ")
        droneIP = input("specify drone IP address: ")
        shippingAddress = input("specify shipping address: ")
        client.deliver(shippingAddress, droneIP)
    elif(cmd == 'help'):
        printCMDlist()
    else:
        print("Unknown CMD number, type 'help' for CMDs list")
