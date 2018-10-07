import socket
import json
import math
import random
from threading import Timer
import numpy as np
import scipy.stats as stats

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
        
        # simdilik asagidaki 3 parametrenin mean ve deviation'ini manuel olarak burdan verelim
        # ilerleyen durumda load_generator.py'den ve rrh.py'dan parametre olarak aliriz
        self.setDemandAndSize()
        #self.cpuDemand = options['cpuDemand']
        #self.memoryDemand = options['memoryDemand']
        #self.packetSize = options['packetSize']
        

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
        self.setDemandAndSize()
    
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
            # burda yeni fieldleri kullanarak cpu demand , packet size ve memory demand 3 farkli field doldurman lazim.
            'cpuDemand': self.cpuDemand,
            'memoryDemand': self.memoryDemand,
            'packetSize': self.packetSize

        }) + "\n"

    def setDemandAndSize(self):
        self.cpuDemand = self.getGaussianRandom(mean = 10000, dev = 3000)
        self.memoryDemand = self.getGaussianRandom(mean = 100000, dev = 30000)
        self.packetSize = self.getGaussianRandom(mean = 1000, dev = 200, max_limit = 1024)
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
            'sequenceNumber': self.sequenceNumber,
            'cpuDemand': self.cpuDemand,
            'memoryDemand': self.memoryDemand,
            'packetSize': self.packetSize
        }
