import math
import random
from .udp_connection import UDPConnection

class RRH():
    nextId = -1

    def getNextId():
        RRH.nextId += 1
        return RRH.nextId

    def __init__(self, options):
        self.id = options['id']
        self.dstPort = options['dstPort']
        self.dstIP = options['dstIP']
        self.connections = []
        self.state = 'stopped'
        self.arrivalRate = options['arrivalRate']
        self.addConnection(options['connectionNumber'])

    def addConnection(self, amount=1):
        for idx in range(amount):
            connection = UDPConnection({
                'name': 'rrh#' + str(self.id) + 'connection#' + str(RRH.getNextId()),
                'dstIP': self.dstIP,
                'dstPort': self.dstPort,
                'arrivalRate': self.arrivalRate
            })
            self.connections.append(connection)

    def removeConnection(self, amount=1):
        for idx in range(amount):
            connection = self.connections.pop()
            connection.close()

    def setArrivalRate(self, rate):
        self.arrivalRate = rate
        for connection in self.connections:
            connection.setArrivalRate(rate)

    def stop(self):
        for connection in self.connections:
            connection.stop()
        self.state = 'stopped'

    def start(self):
        for connection in self.connections:
            connection.start()
        self.state = 'running'

    def destroy(self):
        for connection in self.connections:
            connection.close()

    def toObject(self):
       return {
           'id': self.id,
           'dstPort': self.dstPort,
           'arrivalRate': self.arrivalRate,
           'connections': [connection.toObject() for connection in self.connections],
           'state': self.state
       }
