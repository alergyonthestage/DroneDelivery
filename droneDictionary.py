import datetime

class DroneDictionary:
    availableDrones = {}
    busyDrones = {}
    
    def getAvailableDrones(self):
        return self.availableDrones.items()
    
    def getAvailableDroneInfos(self, droneIP):
        return self.availableDrones.get(droneIP)
    
    def getBusyDroneInfos(self, droneIP):
        return self.busyDrones.get(droneIP)
    
    def isDroneBusy(self, droneIP):
        return self.busyDrones.has_Key(droneIP)
    
    def isDroneAvailable(self, droneIP):
        return self.availableDrones.has_Key(droneIP)
    
    def isDroneUnavailable(self, droneIP):
        return not self.isDroneBusy() and not self.isDroneAvailable()
    
    def addAvailableDrone(self, droneIP, droneName, dronePort):
        if(self.isDroneUnavailable(droneIP)):
            self.availableDrones[droneIP] = {'name' : droneName, 'port' : dronePort, 'addTime' : datetime.now()}
            return True
        else:
            return False
        
    def removeUnavailableDrone(self, droneIP):
        return self.availableDrones.pop(droneIP)
    
    def moveToBusyDrones(self, droneIP):
        if(self.isDroneAvailable()):
            drone = self.availableDrones.pop(droneIP)
            drone.update({'addTime' : datetime.now()})
            self.busyDrones.update({droneIP : drone})
            return True
        return False
        
    def moveToAvailableDrones(self, droneIP):
        if(self.isDroneBusy()):
            drone = self.busyDrones.pop(droneIP)
            drone.update({'addTime' : datetime.now()})
            self.availableDrones.update({droneIP : drone})
            return True
        return False 
    
    def updateDroneInfos(self, droneIP, dronePort, droneName):
        if(self.isDroneUnavailable(droneIP)):
            return False
        else:
            if(self.isDroneAvailable(droneIP)):
                drone = self.getAvailableDroneInfos(droneIP)
                drone.update({'name' : droneName, 'port' : dronePort})
                self.availableDrones.update({droneIP : drone})
            if(self.isDroneBusy(droneIP)):
                drone = self.getBusyDroneInfos(droneIP)
                drone.update({'name' : droneName, 'port' : dronePort})
                self.busyDrones.update({droneIP : drone})
            return True
