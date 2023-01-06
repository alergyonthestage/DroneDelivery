from droneSideGateway import DroneSideGateway
from clientSideGateway import ClientSideGateway, AnotherClientConnected
from deliveriesRegistry import DeliveriesRegisrty

class Gateway:
    deliveriesRegistry = DeliveriesRegisrty()
    
    def __init__(self, droneGatewayAddress, clientGatewayAddress):
        self.droneSideGateway = DroneSideGateway(*droneGatewayAddress, self.deliveriesRegistry)
        self.clientSideGateway = ClientSideGateway(*clientGatewayAddress, self.deliveriesRegistry, self.droneSideGateway.getDroneDictionary())
    
    def connectAndHandleClient(self):
        try:
            self.clientSideGateway.handleClient()
        except AnotherClientConnected as e:
            print("Cannot connect a new Client!", e)

droneGatewayAddress = ('', 50000)
clientGatewayAddress = ('', 51000)
gateway = Gateway(droneGatewayAddress, clientGatewayAddress)

while True:
    gateway.connectAndHandleClient()
    print("Client Disconnected! Wait for another TCP client request...")
