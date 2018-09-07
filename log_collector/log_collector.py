class LogCollector():
    CAPACITY = 1000

    def __init__(self):
        self.history = []

    def findLastSeen(self, timestamp):
        index = 0
        for entry in self.history:
            if entry['timestamp'] <= timestamp:
                return index
            index += 1
        return index

    def append(self, entry):
        self.history.insert(0, entry)
        if (len(self.history) > LogCollector.CAPACITY):
            self.history.pop()
        return entry

    def peek(self, timestamp = 0):
        return self.history[0:self.findLastSeen(timestamp)]
