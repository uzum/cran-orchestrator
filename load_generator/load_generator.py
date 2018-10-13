from .rrh import RRH
from .config import *
import socket

class LoadGenerator():
    nextId = -1

    def getNextId():
        LoadGenerator.nextId += 1
        return LoadGenerator.nextId

    def __init__(self, rrhNumber=RRH_NUMBER, connectionNumber=CONNECTION_NUMBER,
                 arrivalRate=POISSON_RATE, packetSizeMean=PACKET_SIZE_MEAN, packetSizeDev=PACKET_SIZE_DEV):
        self.rrhs = []
        for idx in range(rrhNumber):
            id = LoadGenerator.getNextId()
            self.rrhs.append(RRH({
                'id': id,
                'dstPort': BASE_PORT + id + 1,
                'dstIP': BROADCAST_ADDRESS,
                'connectionNumber': connectionNumber,
                'arrivalRate': arrivalRate,
                'packetSizeMean': packetSizeMean,
                'packetSizeDev': packetSizeDev
            }))

    def removeRRH(self, rrhId):
        print("removing rrh#" + str(rrhId))
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.destroy()
        self.rrhs = [rrh for rrh in self.rrhs if rrh.id != rrhId]

    def addRRH(self, arrivalRate=POISSON_RATE, packetSizeMean=PACKET_SIZE_MEAN, packetSizeDev=PACKET_SIZE_DEV):
        id = LoadGenerator.getNextId()
        rrh = RRH({
            'id': id,
            'dstPort': BASE_PORT + id + 1,
            'dstIP': BROADCAST_ADDRESS,
            'connectionNumber': 0,
            'arrivalRate': arrivalRate,
            'packetSizeMean': packetSizeMean,
            'packetSizeDev': packetSizeDev
        })
        self.rrhs.append(rrh)
        return rrh.toObject()

    def stopRRH(self, rrhId):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.stop()
                return rrh.toObject()

    def startRRH(self, rrhId):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.start()
                return rrh.toObject()

    def setArrivalRate(self, rrhId, rate):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.setArrivalRate(rate)
                return rrh.toObject()

    def setParameter(self, rrhId, param, value):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.setParameter(param, value)
                return rrh.toObject()

    def addConnection(self, rrhId, amount):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.addConnection(amount)
                return rrh.toObject()

    def removeConnection(self, rrhId, amount):
        for rrh in self.rrhs:
            if (rrh.id == rrhId):
                rrh.removeConnection(amount)
                return rrh.toObject()

    def getConfiguration(self):
        configuration = []
        for rrh in self.rrhs:
            configuration.append(rrh.toObject())
        return configuration
