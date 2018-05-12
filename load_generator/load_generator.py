from .rrh import RRH
from .config import *

class LoadGenerator():
    nextId = -1

    def getNextId():
        LoadGenerator.nextId += 1
        return LoadGenerator.nextId

    def __init__(self, rrhNumber=RRH_NUMBER, connectionNumber=CONNECTION_NUMBER):
        self.rrhs = []
        for idx in range(rrhNumber):
            id = LoadGenerator.getNextId()
            self.rrhs.append(RRH({
                'id': id,
                'dstPort': BASE_PORT + id + 1,
                'dstIP': TARGET_IP,
                'connectionNumber': connectionNumber
            }))

    def removeRRH(self, rrhId):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.destroy()
        self.rrhs = [rrh for rrh in self.rrhs if rrh.id != rrhId]

    def addRRH(self):
       id = LoadGenerator.getNextId()
       self.rrhs.append(RRH({
           'id': id,
           'dstPort': BASE_PORT + id + 1,
           'dstIP': TARGET_IP,
           'connectionNUmber': 0
       }))

    def addConnection(self, rrhId, amount):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.addConnection(amount)

    def removeConnection(self, rrhId, amount):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.removeConnection(amount)

    def getConfiguration(self):
        configuration = []
        for rrh in self.rrhs:
            configuration.append(rrh.toObject())
        return configuration
