import socket
import argparse
from threading import Timer

REPORT_INTERVAL = 10.0

parser = argparse.ArgumentParser()
parser.add_argument("port")
args = parser.parse_args()

reportTimer = None
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', int(args.port)))

def report():
    print('reporting to log-collector')
    timer = Timer(REPORT_INTERVAL, report)
    timer.start()

print('listening to ' + args.port)
report()

while True:
    (message, address) = server_socket.recvfrom(1024)
    print('received message from ' + str(address))
    print(message.decode('utf-8'))
