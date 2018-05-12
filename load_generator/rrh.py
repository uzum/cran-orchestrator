import math
import random
from .udp_connection import UDPConnection

class RRH():
    def __init__(self, options):
        self.id = options['id']
        self.dstPort = options['dstPort']
        self.dstIP = options['dstIP']
        self.connections = []
        self.addConnection(options['connectionNumber'])

    def addConnection(self, amount=1):
        for idx in range(amount):
            connection = UDPConnection({
                'name': 'rrh#' + str(self.id) + 'connection#' + str(idx),
                'dstIP': self.dstIP,
                'dstPort': self.dstPort
            })
            connection.start()
            self.connections.add(connection)
    def removeConnection(self, amount=1):
        connection = self.connections.pop()
        connection.close()

    def destroy(self):
        for connection in self.connections:
            connection.close()