import time

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
