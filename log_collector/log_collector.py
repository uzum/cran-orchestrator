import requests
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

    def notify(self, address):
        return requestPost('/resource-mapper/topology/bbu-migration?address=' + address)

class LogCollector():
    CAPACITY = 1000

    def __init__(self):
        self.history = []
        self.watchlist = []
        self.RMAPI = RMAPI()

    def findLastSeen(self, timestamp):
        index = 0
        for entry in self.history:
            if entry['timestamp'] <= timestamp:
                return index
            index += 1
        return index

    def append(self, entry):
        self.history.insert(0, entry)
        for bbuAddress in self.watchlist:
            if (bbuAddress == entry.address):
                self.RMAPI.notify(entry.address)
                self.watchlist.remove(bbuAddress)

        if (len(self.history) > LogCollector.CAPACITY):
            self.history.pop()
        return entry

    def peek(self, timestamp = 0):
        return self.history[0:self.findLastSeen(timestamp)]

    def watch(self, address):
        self.watchlist.append(address)
