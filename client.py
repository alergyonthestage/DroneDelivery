from socket import socket, AF_INET,SOCK_STREAM
from message import Message, START_CONN, CLOSE_CONN, EXCEPTION, LIST_DRONES

class Client:
    def receiveMessage(self):
        try:
            msgBytes = self.clientSocket.recv(2048)
            print("recived msg", msgBytes)
            msg = Message.fromBytes(msgBytes)
            print("msg unpacked")
            print(msg)
            print(msg.getCmd(), msg.getData())
            return msg.getCmd(), msg.getData()
        except Exception as e:
            print("Exception!", e)
        
    def connect(self, serverName, serverPort):
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((serverName, serverPort))
        print("Wait for confirm to connect")
        replyCmd, replyData = self.receiveMessage()
        if (replyCmd == START_CONN):
            print("Connected!")
            return True
        elif (replyCmd == CLOSE_CONN):
            socket.close()
            print("Connection denied!")
            return False
        else:
            print("Unexpected command recived!")
            return False
        
    def closeConnection(self):
        self.clientSocket.send(Message(CLOSE_CONN, '').getBytes())
        replyCmd, replyData = self.receiveMessage()
        if (replyCmd == CLOSE_CONN):
            self.clientSocket.close()
            print("Connection closed!")
            return True
        elif (replyCmd == EXCEPTION):
            print("Failure, connection mantained!", replyData)
            return False
        else:
            print("Unexpected command recived")
            return False
        
    def getAvailableDrones(self):
        self.clientSocket.send(Message(LIST_DRONES, '').getBytes())
        replyCmd, replyData = self.receiveMessage()
        if (replyCmd == LIST_DRONES):
            print(replyData)
        elif (replyCmd == EXCEPTION):
            print("Exception, could not list available Drones! {}", replyData)
            return False
        else:
            print("Unexpected command recived")
            return False
        
client = Client()
client.connect('', 12000)
client.getAvailableDrones()
client.closeConnection()
