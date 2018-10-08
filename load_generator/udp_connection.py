import socket
import json
import math
import time
import random
from threading import Timer

def nextTime(rate):
    return -math.log(1.0 - random.random()) / rate

class UDPConnection():
    def __init__(self, options):
        self.name = options['name']
        self.dstIP = options['dstIP']
        self.dstPort = options['dstPort']
        self.arrivalRate = options['arrivalRate']
        self.sequenceNumber = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.nextPacketScheduler = None

    def sendPacket(self):
        self.send(self.createPayload())
        interval = nextTime(self.arrivalRate)
        print("next packet from socket" + self.name + " will be sent in " + str(interval) + " seconds")
        self.nextPacketScheduler = Timer(interval, self.sendPacket)
        self.nextPacketScheduler.start()

    def send(self, message):
        print('sending to ' + str(self.dstIP) + ':' + str(self.dstPort) + ' from ' + self.name)
        self.socket.sendto(bytes(message, 'UTF-8'), (self.dstIP, self.dstPort))
        self.sequenceNumber = self.sequenceNumber + 1

    def setArrivalRate(self, rate):
        self.arrivalRate = rate;
        if (self.nextPacketScheduler is not None):
            self.nextPacketScheduler.cancel()
            self.sendPacket()

    def close(self):
        print('closing socket ' + self.name)
        self.nextPacketScheduler.cancel()
        self.nextPacketScheduler = None
        self.socket.close()

    def start(self):
        self.sendPacket()

    def stop(self):
        if (self.nextPacketScheduler is not None):
            self.nextPacketScheduler.cancel()
            self.nextPacketScheduler = None

    def createPayload(self):
        return json.dumps({
            'name': self.name,
            'seq': self.sequenceNumber,
            'timestamp': int(time.time())
        }) + "\n"

    def toObject(self):
        return {
            'name': self.name,
            'sequenceNumber': self.sequenceNumber
        }
