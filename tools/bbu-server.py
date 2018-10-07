
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

# bu port 3000 orjinalinde, 3001 yapcez
UDP_LISTEN_PORT = 3001
REPORT_INTERVAL = 10.0
IP_ADDRESS = subprocess.check_output(['hostname', '-I']).decode().split(' ')[0]

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('address')
args = parser.parse_args()

timer = None
packetCount = 0
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
            'packetCount': packetCount,
            'cpuUtilization': cpuUtilization,
            'memoryUtilization': memoryUtilization
        }
        request = urllib.request.Request(args.address, json.dumps(payload).encode('utf-8'), { 'Content-Type': 'application/json' })
        response = urllib.request.urlopen(request)
    except Exception as err:
        print('failed to send report')
        print(err)
    timer = Timer(REPORT_INTERVAL, report)
    timer.start()

print('listening to ' + str(UDP_LISTEN_PORT))
# asagiyi log collector istemedigin icin calistirmiyorsun 
#report()

while True:
    (message, address) = server_socket.recvfrom(1024)
    packetCount += 1
    print('received message from ' + str(address))
    # Burda arkada caliscak CPU & memory allocation sciptini calistirman lazim
    # background process olarak calistirman onemli cunku bu kodun devam etmesi lazim 
    # message json parse ile parse edilcek ve cpu demand ve memory demand olculecek.
    print(message.decode('utf-8'))
