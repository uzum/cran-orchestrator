import subprocess
import os
import time
import argparse
import json
import urllib.request
from nwstats import NetworkStats
from threading import Timer

REPORT_INTERVAL = 2.0
IP_ADDRESS = subprocess.check_output(['hostname', '-I']).decode().split(' ')[0]

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('address')
parser.add_argument('interface')
args = parser.parse_args()

timer = None
nwStats = NetworkStats(args.interface)

def report():
    try:
        cpuUtilization = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()))
        total, used, free = list(map(int, os.popen('free -t -m').readlines()[-1].split()[1:]))
        memoryUtilization = round(float(used)/total, 2) * 100
        payload = {
            'source': args.name,
            'address': IP_ADDRESS,
            'timestamp': int(time.time()),
            'cpuUtilization': cpuUtilization,
            'memoryUtilization': memoryUtilization
        }
        payload.update(nwStats.collect())
        request = urllib.request.Request(args.address, json.dumps(payload).encode('utf-8'), { 'Content-Type': 'application/json' })
        response = urllib.request.urlopen(request)
    except Exception as err:
        print('failed to send report')
        print(err)
    timer = Timer(REPORT_INTERVAL, report)
    timer.start()

report()
