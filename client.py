from socket import socket, AF_INET,SOCK_STREAM
from message import Message, START_CONN, CLOSE_CONN, EXCEPTION, LIST_DRONES, DELIVER

DEBUG = False

class Client:
    def _sendMessage(self, cmd, data):
        if(DEBUG):
            print("DEBUG - Sending MSG to gateway...")
        try:
            msgBytes = Message(cmd, data).getBytes()
            self.clientSocket.send(msgBytes)
            if(DEBUG):
                print("DEBUG - MSG: '", cmd, " - ", data, "' sent to gateway")
        except Exception as e:
            print("Cannot send Message: [", cmd, " - ", data, "]. Exception: ", e)
    
    def _receiveMessage(self):
        if(DEBUG):
            print("DEBUG - Reciving MSG from gateway...")
        try:
            msgBytes = self.clientSocket.recv(2048)
            msg = Message.fromBytes(msgBytes)
            if(DEBUG):
                print("DEBUG - MSG: '", msg.getCmd(), " - ", msg.getData(), "' recived from gateway")
            return msg.getCmd(), msg.getData()
        except Exception as e:
            print("Cannot recive Messages. Exception: ", e)
            
    def _emergencyCloseConnection(self):
        #TO-DO implement try send CLOSE_CONN and then close, else if already disconnected close socket
        self.clientSocket.close()
        
    def connectToGateway(self, serverName, serverPort):
        try:
            self.clientSocket = socket(AF_INET, SOCK_STREAM)
            self.clientSocket.connect((serverName, serverPort))
        except Exception as e:
            print("Cannot connect to gateway. Exception: ", e)
        print("Waiting the gateway to accept the connection...")
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
        print("Asking the gateway to close the connection...")
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
            print("Available drones list: \n" + replyData)
        elif (replyCmd == EXCEPTION):
            print(replyData)
            return False
        else:
            print("Unexpected command recived! Packet discarted.")
            return False
        
    def deliver(self, shippingAddress, droneIP):
        msgData = droneIP + "_" + shippingAddress
        self._sendMessage(DELIVER, msgData)      
        
        
#------------  APP CLIENT  -----------

quitApp = False

def printCMDlist():
    print("CMD NUMBERS: \n" + 
          "0 -> disconnect from gateway and quit client APP \n" +
          "1 -> list available drones \n" +
          "2 -> ask for delivery\n")

client = Client()
print("Connecting...")
client.connectToGateway('', 51000)
printCMDlist()
while not quitApp:
    cmd = input("\nInsert CMD number: ")
    print("\n")
    if(cmd == '0'):
        print("Closing connection with gateway and quitting client APP.")
        client.closeConnection()
        quitApp = True
    elif(cmd == '1'):
        print("AVAILABLE DRONES\n")
        client.getAvailableDrones()
    elif(cmd == '2'):
        print("NEW DELIVERY REQUEST\n")
        droneIP = input("Please, specify drone IP address: ")
        shippingAddress = input("Please, specify shipping address: ")
        print("\n")
        client.deliver(shippingAddress, droneIP)
        print("Delivery requested to drone: ", droneIP)
    elif(cmd == 'help'):
        printCMDlist()
    else:
        print("Unknown CMD number, type 'help' for CMDs list")
