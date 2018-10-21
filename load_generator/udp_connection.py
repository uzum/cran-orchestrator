import socket
import json
import math
import time
import random
from threading import Timer
import numpy as np
import scipy.stats as stats
from .config import *

def nextTime(rate):
    return -math.log(1.0 - random.random()) / rate

class UDPConnection():
    def __init__(self, options):
        self.name = options['name']
        self.dstIP = options['dstIP']
        self.dstPort = options['dstPort']
        self.arrivalRate = options['arrivalRate']
        self.packetSizeMean = options['packetSizeMean']
        self.packetSizeDev = options['packetSizeDev']
        self.sequenceNumber = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.nextPacketScheduler = None

    def sendPacket(self):
        self.send(self.createPayload())
        interval = nextTime(self.arrivalRate)
        if (DEBUG): print("next packet from socket" + self.name + " will be sent in " + str(interval) + " seconds")
        self.nextPacketScheduler = Timer(interval, self.sendPacket)
        self.nextPacketScheduler.start()

    def send(self, message):
        if (DEBUG): print('sending to ' + str(self.dstIP) + ':' + str(self.dstPort) + ' from ' + self.name)
        self.socket.sendto(bytes(message, 'UTF-8'), (self.dstIP, self.dstPort))
        self.sequenceNumber = self.sequenceNumber + 1

    def setParameter(self, param, value):
        setattr(self, param, value)

    def setArrivalRate(self, rate):
        self.arrivalRate = rate;
        if (self.nextPacketScheduler is not None):
            self.nextPacketScheduler.cancel()
            self.sendPacket()

    def close(self):
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
        packetSize = self.getPacketSize()
        if (DEBUG): print('sending a packet with ' + str(packetSize) + ' bytes payload')
        return json.dumps({
            'name': self.name,
            'seq': self.sequenceNumber,
            'packetSize': packetSize,
            'data': 'a' * (packetSize - 49), # The reason we use -49 is to compansate string length with the desired packet size in terms of bytes.
            'timestamp': int(time.time())
        }) + "\n"

    def getPacketSize(self):
        return self.getGaussianRandom(mean = self.packetSizeMean, dev = self.packetSizeDev, max_limit = PACKET_SIZE_MAX)

    def getGaussianRandom(self, mean, dev, max_limit = None, min_limit = 0):
        # returns number of cycles in terms of kHz
        if max_limit == None:
            return int (np.random.normal(mean,dev,1))
        else:
            return int( stats.truncnorm(
                (min_limit - mean) / dev, (max_limit - mean) / dev, loc = mean, scale = dev ).rvs(1) )

    def toObject(self):
        return {
            'name': self.name,
            'sequenceNumber': self.sequenceNumber
        }
