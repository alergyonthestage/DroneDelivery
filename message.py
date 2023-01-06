#commands (cmd) to use for messages
START_CONN = "START_CONN"
CLOSE_CONN = "CLOSE_CONN"
LIST_DRONES = "LIST_DRONES"
DELIVER = "DELIVER"
EXCEPTION = "EXCEPTION"
AVAILABLE = "AVAILABLE"
UNAVAILABLE = "UNAVAILABLE"
BUSY = "BUSY"

class Message:
    def __init__(self, cmd, data):
        self.cmd = str(cmd)
        self.data = str(data)

    @classmethod
    def fromBytes(self, msgBytes):
        message = msgBytes.decode()
        args = message.split("-")
        return Message(args[0], args[1])
        
    def getCmd(self):
        return self.cmd
    
    def getData(self):
        return self.data
    
    def getBytes(self):
        message = self.cmd + "-" + self.data
        return message.encode()

