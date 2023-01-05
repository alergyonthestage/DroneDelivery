import datetime

class DeliverHandler:
    REQUESTED = 'REQUESTED'
    DELIVERING = 'DELIVERING' 
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'
    pendingDeliveries = {}
    deliveryHistory = {}
    
    def addPendingDelivery(self, droneIP, shippingAddress):
        if(self.pendingDeliveries.has_key(droneIP)):
            return False
        timestamp = datetime.now()
        self.pendingDeliveries[droneIP] = {'status' : self.REQUESTED, 'shippingAddress' : shippingAddress, 'requested' : timestamp}
        return True
        
    def delivering(self, droneIP):
        if(self.pendingDeliveries.has_key(droneIP)):
            timestamp = datetime.now()
            delivery = self.pendingDeliveries.get(droneIP)
            delivery.update({'status' : self.DELIVERING, 'delivering' : timestamp})
            self.pendingDeliveries.update({droneIP : delivery})
            return True
        return False
    
    def delivered(self, droneIP):
        if(self.pendingDeliveries.has_key(droneIP)):
            timestamp = datetime.now()
            delivery = self.pendingDeliveries.pop(droneIP)
            delivery.update({'status' : self.DELIVERED})
            self.deliverHistory.update({(droneIP, timestamp) : delivery})
            return True
        return False
   
    def cancelled(self, droneIP):
        if(self.pendingDeliveries.has_key(droneIP)):
            timestamp = datetime.now()
            delivery = self.pendingDeliveries.pop(droneIP)
            delivery.update({'status' : self.CANCELLED})
            self.deliverHistory.update({(droneIP, timestamp) : delivery})
            return True
        return False

    