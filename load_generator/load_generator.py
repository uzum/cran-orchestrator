from .rrh import RRH
from .config import *

class LoadGenerator():
    def __init__(self, rrhNumber=RRH_NUMBER, connectionNumber=CONNECTION_NUMBER):
        self.rrhs = []
        for idx in range(rrhNumber):
            rrh = RRH({
                'id': idx,
                'dstPort': BASE_PORT + idx + 1,
                'dstIP': TARGET_IP,
                'connectionNumber': connectionNumber
            })