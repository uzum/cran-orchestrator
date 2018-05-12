import socket
import json
import math
import random
from threading import Timer
from .config import *

def nextTime(rate):
    return -math.log(1.0 - random.random()) / rate

class UDPConnection():
    def __init__(self, options):
        self.name = options['name']
        self.dstIP = options['dstIP']
        self.dstPort = options['dstPort']
        self.sequenceNumber = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def sendPacket(self):
        self.send(self.createPayload())
        interval = nextTime(POISSON_RATE)
        print("next packet from socket" + self.name + " will be sent in " + str(interval) + " seconds")
        Timer(interval, self.sendPacket).start()

    def send(self, message):
        print('sending to ' + str(self.dstIP) + ':' + str(self.dstPort) + ' from ' + self.name)
        self.socket.sendto(bytes(message, 'UTF-8'), (self.dstIP, self.dstPort))
        self.sequenceNumber = self.sequenceNumber + 1

    def close(self):
        print('closing socket ' + self.name)
        self.socket.close()

    def createPayload(self):
        return json.dumps({
            'name': self.name,
            'seq': self.sequenceNumber    
        }) + "\n"

    def start(self):
        self.sendPacket()
