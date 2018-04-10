import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("port")
args = parser.parse_args()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', int(args.port)))

print('listening to ' + args.port)
while True:
    (message, address) = server_socket.recvfrom(1024)
    print('received message from ' + str(address))
    print(message.decode('utf-8'))
