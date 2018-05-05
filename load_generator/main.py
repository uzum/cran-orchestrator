from threading import Timer
from functools import partial
from udp_socket import UDPSocket
import math
import random
import json
from config import *

def createPayload(socket):
    return json.dumps({
      'rrh': socket.rrh,
      'connection': socket.connection,
      'sequenceNumber': socket.sequenceNumber
    })

def nextTime(rate):
    return -math.log(1.0 - random.random()) / rate

if __name__ == "__main__":
    def sendMessage(socket):
        socket.send(createPayload(socket))
        interval = nextTime(POISSON_RATE)
        print("next packet from " + socket.name + " will be sent in " + str(interval) + " seconds")
        Timer(interval, partial(sendMessage, socket)).start()

    for idx in range(RRH_NUMBER):
        for connIdx in range(CONNECTION_NUMBER):
            udp_socket = UDPSocket({
                'rrh': idx,
                'connection': connIdx,
                'name': 'RRH#' + str(idx) + 'CONN#' + str(connIdx),
                'port': BASE_PORT + idx + 1,
                'ip': TARGET_IP
            })
            sendMessage(udp_socket)
