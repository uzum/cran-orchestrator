# in order to run the code : 
# python3 bbu-server.py bbu-name x


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
# bu port 3000 orjinalinde, 3001 yapcez
UDP_LISTEN_PORT = 3001
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
packetCount = 0
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', UDP_LISTEN_PORT))


print('listening to ' + str(UDP_LISTEN_PORT))
# asagiyi log collector istemedigin icin calistirmiyorsun 
#report()

while True:
    # Burda arkada caliscak CPU & memory allocation sciptini calistirman lazim
    # background process olarak calistirman onemli cunku bu kodun devam etmesi lazim 
    # message json parse ile parse edilcek ve cpu demand ve memory demand olculecek.
    
    (message, address) = server_socket.recvfrom(1024)
    #timestamp = int(time.time())

    # parse the udp packet payload to retrieve relevant values
    try:
        payload = json.loads(message.decode('utf-8'))
        localStats['packetCount'] += 1
        # calculate how much time has passed since the packet was created in load generator
        #localStats['totalLatency'] += (timestamp - payload['timestamp'])
        allocator = Allocator(payload)
        allocator.start()
    except Exception as err:
        print('failed to process UDP packet')
        print(err)