import random

frac_slow = 0.5
TXN_size = 1024 * 8			# 1kB
MB2b = 1024 * 1024 * 8		# Convert MB to bits

block_ID_size = 0x11111111	# 32 bit ID for blocks
TXN_ID_size = 0x11111111	# 32 bit ID for TXN

tasks = {}

# Node class to store each peer
class node:
	
	# Initialize
	def __init__(self,uniqueID,ia_time):
		self.uniqueID = uniqueID
		self.fast = (random.random()>frac_slow)
		self.ia_time = ia_time
		self.pending_TXN = {}
		self.peers = {}

	# Handle to add new peer 
	def add_peer(self,peer):
		self.peers[peer.uniqueID] = [random.uniform(0.001,0.5),MB2b*(5+95*(self.fast and peer.fast))]

	# Generate a new transaction
	def generateTransaction(self, payee_ID, amount):

		# Time for next TXN
		next_event_time = random.expovariate(1/self.ia_time)

		# Unique TXN_ID (as random, assuming collision resistance)
		TXN_ID = random.randint(1,TXN_ID_size)

		# Add TXN generation to list of tasks
		tasks[next_event_time] = str(TXN_ID) + ": " + str(self.uniqueID) + " pays " + str(payee_ID) + " "+str(amount)+" coins"
		
		# Update own set of pending TXN
		self.pending_TXN[TXN_ID] = tasks[next_event_time]

		# Broadcast to peers
		self.broadcastTransaction(tasks[next_event_time],next_event_time)
		return tasks[next_event_time]

	def broadcastTransaction(self, TXN, start_time):
		for peer in self.peers:
			tasks[self.peers[peer][0]+ TXN_size/self.peers[peer][1] +\
			 random.expovariate(self.peers[peer][1]/(96*1024)) + start_time]\
			 = "ReceiveTXN: "+str(peer)+" " + TXN


class block:

	def __init__(self, prev_block):
		self.prev_block = prev_block
		self.uniqueID = random.randint(1,block_ID_size)

class genesisBlock:

	def __init__(self):
		self.uniqueID = 0

class graph:
	def __init__(self):
		pass