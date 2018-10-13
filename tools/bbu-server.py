import socket
import os
import time
import argparse
import json
import urllib.request
import subprocess
from threading import Timer
from nwstats import NetworkStats
from allocator import Allocator
UDP_LISTEN_PORT = 3000
REPORT_INTERVAL = 2.0
IP_ADDRESS = subprocess.check_output(['hostname', '-I']).decode().split(' ')[0]

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('address')
parser.add_argument('interface')
args = parser.parse_args()

timer = None
nwStats = NetworkStats(args.interface)
localStats = {
    'packetCount': 0,
    'totalLatency': 0
}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', UDP_LISTEN_PORT))

def report():
    try:
        cpuUtilization = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()))
        total, used, free = list(map(int, os.popen('free -t -m').readlines()[-1].split()[1:]))
        memoryUtilization = round(float(used)/total, 2) * 100
        payload = {
            'source': args.name,
            'address': IP_ADDRESS,
            'timestamp': int(time.time()),
            'packetPerSecond': localStats['packetCount'] / REPORT_INTERVAL,
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

        request = urllib.request.Request(args.address, json.dumps(payload).encode('utf-8'), { 'Content-Type': 'application/json' })
        response = urllib.request.urlopen(request)
    except Exception as err:
        print('failed to send report')
        print(err)
    timer = Timer(REPORT_INTERVAL, report)
    timer.start()
    # restart packet count and latency calculations before next iteration
    localStats['packetCount'] = 0
    localStats['totalLatency'] = 0

print('listening to ' + str(UDP_LISTEN_PORT))
report()

while True:
    (message, address) = server_socket.recvfrom(1024)
    timestamp = int(time.time())

    # parse the udp packet payload to retrieve relevant values
    try:
        payload = json.loads(message.decode('utf-8'))
        localStats['packetCount'] += 1
        # calculate how much time has passed since the packet was created in load generator
        localStats['totalLatency'] += (timestamp - payload['timestamp'])
        allocator = Allocator(payload)
        allocator.start()
    except Exception as err:
        print('failed to process UDP packet')
        print(err)