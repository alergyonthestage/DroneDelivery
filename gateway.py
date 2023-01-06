from droneSideGateway import DroneSideGateway
from clientSideGateway import ClientSideGateway, AnotherClientConnected
from deliveriesRegistry import DeliveriesRegisrty

class Gateway:
    clientConnected = False
    deliveriesRegistry = DeliveriesRegisrty()
    
    def __init__(self, droneGatewayAddress, clientGatewayAddress):
        self.droneSideGateway = DroneSideGateway(*droneGatewayAddress, self.deliveriesRegistry)
        self.clientSideGateway = ClientSideGateway(*clientGatewayAddress, self.deliveriesRegistry, self.droneSideGateway.getDroneDictionary())
        
    def isClientConnected(self):
        return self.clientConnected
    
    def connectClient(self):
        try:
            self.clientSideGateway.handleClient()
        except AnotherClientConnected as e:
            print("Client Not Connected!", e)

droneGatewayAddress = ('', 50000)
clientGatewayAddress = ('', 51000)
gateway = Gateway(droneGatewayAddress, clientGatewayAddress)

while True:
    if(not gateway.isClientConnected()):
        gateway.connectClient()
