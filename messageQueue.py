class Nodo:
  def __init__(self, message=None, nextNode=None):
    self.message = message
    self.nextNode  = nextNode
    
  def __str__(self):
    return str(self.message)

class Coda:
  def __init__(self):
    self.length = 0
    self.head = None
    
  def isEmpty(self):
    return (self.length == 0)

  def Inserimento(self, message):
    newNode = Nodo(message)
    newNode.nextNode = None
    if self.head == None:
      # se la lista e’ vuota il nodo e’ il primo
      self.head = Nodo
    else:
      # trova l’ultimo nodo della lista
      last = self.head
      while last.nextNode: last = last.nextNode
      # aggiunge il nuovo nodo
      last.nextNode = newNode
    self.length = self.length + 1
    
  def Rimozione(self):
    message = self.head.message
    self.head = self.head.nextNode
    self.length = self.length - 1
    return message