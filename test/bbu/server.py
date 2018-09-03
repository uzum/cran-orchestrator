import socket
import os
import time
import argparse
import json
import urllib.request
from threading import Timer

REPORT_INTERVAL = 10.0
LOG_COLLECTOR_ADDRESS = 'http://127.0.0.1:5004/log-collector/append'

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("port")
args = parser.parse_args()

reportTimer = None
packetCount = 0
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', int(args.port)))

def report():
    cpuUtilization = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()))
    total, used, free = list(map(int, os.popen('free -t -m').readlines()[-1].split()[1:]))
    memoryUtilization = round(float(used)/total, 2) * 100
    payload = {
        'source': args.name,
        'timestamp': int(time.time()),
        'packetCount': packetCount,
        'cpuUtilization': cpuUtilization,
        'memoryUtilization': memoryUtilization
    }
    request = urllib.request.Request(LOG_COLLECTOR_ADDRESS, json.dumps(payload).encode('utf-8'), { 'Content-Type': 'application/json' })
    response = urllib.request.urlopen(request)
    timer = Timer(REPORT_INTERVAL, report)
    timer.start()

print('listening to ' + args.port)
report()

while True:
    (message, address) = server_socket.recvfrom(1024)
    packetCount += 1
    print('received message from ' + str(address))
    print(message.decode('utf-8'))
