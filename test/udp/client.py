import socket
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("host")
parser.add_argument("port")
args = parser.parse_args()

conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while(True):
    conn.sendto(bytes('Hello from ' + args.name, 'UTF-8'), (args.host, int(args.port)))
    time.sleep(1)
