import subprocess
import os
import time
import argparse
import json
from threading import Timer
import urllib.request

class NetworkStats():
    def __init__(self):
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

    def getInterfaces(self):
        return [iface for iface in os.listdir('/sys/class/net') if iface.startswith('tap')]

    def getStat(self, filename):
        sum = 0
        for iface in self.getInterfaces():
            with open('/sys/class/net/' + iface + '/statistics/' + filename, 'r') as f:
                sum += int(f.read())
        return sum

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

REPORT_INTERVAL = 2.0
IP_ADDRESS = subprocess.check_output(['hostname', '-I']).decode().split(' ')[0]

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('address')
args = parser.parse_args()

timer = None
nwStats = NetworkStats()

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
