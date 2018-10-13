import sys
class Allocator():
	def __init__(self, payload):
		#self.memory = payload['memoryDemand']
		self.memory = 1
		#self.cpu = payload['cpuDemand']
		self.cpu = 1
		# burda packet size ise yaramicak sanirim
		self.packetSize = payload['packetSize']
		self.data = payload['data']
		self.dummy = bytearray(1)
		print ('packet size : ', self.packetSize)
		print ('length of recieved string data : ', len(self.data), ' in bytes : ',sys.getsizeof(self.data))
	def memory_allocate(self):
		self.dummy = bytearray(self.memory)
	def memory_release(self):
		self.dummy = bytearray(1)
	def cpu_allocate(self):
		self.memory_allocate()
		for i in range(self.cpu):
			5*i
		self.memory_release()

	def start(self):
		#print('Allocation Process Started')
		self.cpu_allocate()
		#print('Allocation Completed')