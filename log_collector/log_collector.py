class LogCollector():
    def __init__(self):
        self.history = []

    def append(self, entry):
        self.history.append(entry)
        return entry

    def peek(self, index = 0):
        return self.history[index:]
