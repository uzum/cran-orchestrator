import requests
import time
from .config import *

class RMAPI():
    def __init__(self):
        self.remote = RM_SERVER_IP
        self.port = RM_SERVER_PORT
        self.pathPrefix = 'http://' + self.remote + ':' + self.port

    def requestGet(self, path):
        return requests.get(self.pathPrefix + path)

    def requestPost(self, path, data):
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        return requests.post(self.pathPrefix + path, data=data, headers=headers)

    def notifyMigration(self, address):
        return requestPost('/resource-mapper/topology/bbu-migration?address=' + address)

    def notifyCreation(self, address):
        return requestPost('/resource-mapper/topology/bbu-creation?address=' + address)

class LogCollector():
    CAPACITY = 1000

    def __init__(self):
        self.history = []
        self.watchlist = {
            'migration': [],
            'creation': []
        }
        self.RMAPI = RMAPI()

    def findLastSeen(self, timestamp):
        index = 0
        for entry in self.history:
            if entry['timestamp'] <= timestamp:
                return index
            index += 1
        return index

    def append(self, entry):
        now = int(time.time())
        entry['logLatency'] = now - entry['timestamp']
        entry['timestamp'] = now
        self.history.insert(0, entry)

        for bbuName in self.watchlist['migration']:
            if (bbuName == entry.source):
                self.RMAPI.notifyMigration(entry.address)
                self.watchlist['migration'].remove(bbuName)

        for bbuName in self.watchlist['creation']:
            if (bbuName == entry.source):
                self.RMAPI.notifyCreation(entry.address)
                self.watchlist['creation'].remove(bbuName)

        if (len(self.history) > LogCollector.CAPACITY):
            self.history.pop()
        return entry

    def peek(self, timestamp = 0):
        return self.history[0:self.findLastSeen(timestamp)]

    def stats(self, source, limit = 30):
        excludedAttrs = ['address', 'source', 'timestamp']
        stats = {
            'count': 0
        }
        for entry in self.history:
            if entry['source'] == source:
                stats['count'] = stats['count'] + 1
                if (stats['count'] == limit): break

                for attr, value in entry.items():
                    if attr not in excludedAttrs:
                        if attr not in stats:
                            stats[attr] = {
                                'mean': 0.0,
                                'last5': []
                            }
                        # calculate mean
                        stats[attr]['mean'] = ((stats[attr]['mean'] * (stats['count'] - 1)) + value) / stats['count']
                        # put aside most recent 5 entries
                        if (stats['count'] < 6):
                            stats[attr]['last5'].append(value)
        return stats

    def watch(self, list, name):
        self.watchlist[list].append(name)
