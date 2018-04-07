from threading import Timer
from functools import partial
from udp_socket import UDPSocket
from config import *

if __name__ == "__main__":
    def sendMessage(socket):
        socket.send('hello from ' + socket.name + '\n')
        Timer(SEND_INTERVAL, partial(sendMessage, socket)).start()

    for idx in range(RRH_NUMBER):
        udp_socket = UDPSocket({
            'name': 'RRH#' + str(idx + 1),
            'port': BASE_PORT + idx,
            'ip': TARGET_IP
        })
        sendMessage(udp_socket)
