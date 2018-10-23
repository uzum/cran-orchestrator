import socket
import time
import os
import argparse
import json
import sys
import urllib.request
import subprocess
from threading import Timer

class NetworkStats():
    def __init__(self, interface):
        self.interface = interface
        self.stats = {
            'timestamp': 0,
            'rx_bytes': 0,
            'tx_bytes': 0,
            'rx_packets': 0,
            'tx_packets': 0,
            'rx_dropped': 0,
            'tx_dropped': 0,
            'rx_errors': 0,
            'tx_errors': 0
        }

    def getStat(self, filename):
        with open('/sys/class/net/' + self.interface + '/statistics/' + filename, 'r') as f:
            return int(f.read())

    def collect(self):
        # calculate duration and update timestamp
        timestamp = int(time.time())
        duration = timestamp - self.stats['timestamp']
        self.stats['timestamp'] = timestamp

        stats = {}
        # byte and packet stats, calculate by report interval time
        for stat in ['bytes', 'packets']:
            for rxtx in ['rx', 'tx']:
                key = rxtx + '_' + stat
                currentValue = self.getStat(key)
                stats[key] = (currentValue - self.stats[key]) / duration
                self.stats[key] = currentValue

        # error and drop rate stats, calculate by number of packets
        for stat in ['dropped', 'errors']:
            for rxtx in ['rx', 'tx']:
                key = rxtx + '_' + stat
                # if there were no packets during this interval, rates are 0
                if stats[rxtx + '_packets'] == 0:
                    stats[key] = 0
                else:
                    currentValue = self.getStat(key)
                    stats[key] = (currentValue - self.stats[key]) / stats[rxtx + '_packets']
                    self.stats[key] = currentValue
        return stats

class Allocator():
    def __init__(self, payload):
        self.coefficient = 10
        self.packetSize = payload['packetSize']
        self.dummy = bytearray(1)

    def memory_allocate(self):
        self.dummy = bytearray(self.packetSize * self.coefficient)

    def memory_release(self):
        self.dummy = bytearray(1)

    def cpu_allocate(self):
        self.memory_allocate()
        for i in range(self.packetSize * self.coefficient):
            5*i
        self.memory_release()

    def start(self):
        self.cpu_allocate()

UDP_LISTEN_PORT = 3000
REPORT_INTERVAL = 2.0
GATEWAY_ADDRESS = '10.0.0.2'
IP_ADDRESS = subprocess.check_output(['hostname', '-I']).decode().split(' ')[0]

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('address')
parser.add_argument('interface')
args = parser.parse_args()

timer = None
nwStats = NetworkStats(args.interface)
localStats = {
    'packetBytes': 0,
    'packetCount': 0,
    'totalLatency': 0
}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', UDP_LISTEN_PORT))

def report():
    # ping gateway in each report interval to trigger LLDP after migration/creation
    os.system('ping -c 1 ' + GATEWAY_ADDRESS)
    try:
        cpuUtilization = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()))
        total, used, free = list(map(int, os.popen('free -t -m').readlines()[-1].split()[1:]))
        memoryUtilization = round(float(used)/total, 2) * 100
        payload = {
            'source': args.name,
            'address': IP_ADDRESS,
            'timestamp': int(time.time()),
            'packetPerSecond': localStats['packetCount'] / REPORT_INTERVAL,
            'bytePerSecond': localStats['packetBytes'] / REPORT_INTERVAL,
            'cpuUtilization': cpuUtilization,
            'memoryUtilization': memoryUtilization
        }
        if (localStats['packetCount'] > 0):
            payload['averageLatency'] = localStats['totalLatency'] / localStats['packetCount']
        else:
            # if there has been no packets delivered during this interval, no need to calculate latency
            payload['averageLatency'] = 0

        # add network stats to the payload
        payload.update(nwStats.collect())

        # calculate the rate of processed packets to received packets
        if (payload['rx_packets'] > 0):
            payload['packetDropRate'] = (payload['rx_packets'] - payload['packetPerSecond']) / payload['rx_packets']
        else:
            # if there has been no packets delivered during this interval, no need to calculate drop rate
            payload['packetDropRate'] = 0

        request = urllib.request.Request(args.address, json.dumps(payload).encode('utf-8'), { 'Content-Type': 'application/json' })
        response = urllib.request.urlopen(request)
    except Exception as err:
        print('failed to send report')
        print(err)
    timer = Timer(REPORT_INTERVAL, report)
    timer.start()
    # restart packet count and latency calculations before next iteration
    localStats['packetCount'] = 0
    localStats['packetBytes'] = 0
    localStats['totalLatency'] = 0

print('listening to ' + str(UDP_LISTEN_PORT))
report()

while True:
    (message, address) = server_socket.recvfrom(1024 * 1024)
    timestamp = int(time.time())

    # parse the udp packet payload to retrieve relevant values
    try:
        payload = json.loads(message.decode('utf-8'))
        localStats['packetCount'] += 1
        localStats['packetBytes'] += len(message)
        # calculate how much time has passed since the packet was created in load generator
        localStats['totalLatency'] += (timestamp - payload['timestamp'])
        allocator = Allocator(payload)
        allocator.start()
    except Exception as err:
        print('failed to process UDP packet')
        print(err)
