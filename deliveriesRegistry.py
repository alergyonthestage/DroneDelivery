from queue import Queue
import datetime

class DeliveriesRegisrty:
    REQUESTED = 'REQUESTED'
    DELIVERING = 'DELIVERING' 
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'
    pendingDeliveries = {}
    deliveryHistory = {}
    newRequests = Queue(0)
    
    def requestDelivery(self, droneIP, shippingAddress):
        if(self.pendingDeliveries.has_key(droneIP)):
            return False
        timestamp = datetime.now()
        self.pendingDeliveries[droneIP] = {'status' : self.REQUESTED, 'shippingAddress' : shippingAddress, 'requested' : timestamp}
        self.newRequests.put(droneIP)
        return True
        
    def delivering(self, droneIP):
        if(self.pendingDeliveries.has_key(droneIP)):
            timestamp = datetime.now()
            delivery = self.pendingDeliveries.get(droneIP)
            delivery.update({'status' : self.DELIVERING, 'delivering' : timestamp})
            self.pendingDeliveries.update({droneIP : delivery})
            if(self.newReq > 0):
                self.newReq -= 1
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
    
    def hasNewRequests(self):
        return not self.newRequests.empty()
    
    def getNextRequest(self):
        droneIP = self.newRequests.get()
        return (droneIP, self.pendingDeliveries.get(droneIP))

    def hasPendingDelivery(self, droneIP):
        return self.pendingDeliveries.has_key(droneIP)