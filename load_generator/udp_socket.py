import socket
from config import *

class UDPSocket():
	def __init__(self, options):
		self.name = options['name']
		self.ip = options['ip']
		self.port = options['port']
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def send(self, message):
		print('sending to ' + str(self.ip) + ':' + str(self.port) + ' from ' + self.name)
		self.socket.sendto(bytes(message, 'UTF-8'), (self.ip, self.port))
