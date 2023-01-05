from datetime import datetime 

class DroneDictionary:
    availableDrones = {}
    busyDrones = {}
    
    def addAvailableDrone(self, droneIP, droneName, dronePort):
        if(self.busyDrones.get(droneIP) == None and self.availableDrones.get(droneIP) == None):
            self.availableDrones.update({droneIP : {'name' : droneName, 'port' : dronePort, 'addTime' : datetime.now()}})
            return True
        else:
            return False
        
    def removeUnavailableDrone(self, droneIP):
        return self.availableDrones.pop(droneIP)
    
    def moveToBusyDrones(self, droneIP):
        drone = self.availableDrones.pop(droneIP)
        drone.update({'addTime' : datetime.now()})
        self.busyDrones.update({droneIP : drone})
        
    def moveToAvailableDrones(self, droneIP):
        drone = self.busyDrones.pop(droneIP)
        drone.update({'addTime' : datetime.now()})
        self.availableDrones.update({droneIP : drone})
        
    def getAvailableDroneInfos(self, droneIP):
        return self.availableDrones.get(droneIP)
    
    def getBusyDroneInfos(self, droneIP):
        return self.busyDrones.get(droneIP)