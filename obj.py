import param
import random

# Node class to store each peer
class node:
	
	# Initialize
	def __init__(self,uniqueID,ia_time):
		self.uniqueID = uniqueID
		self.fast = (random.random()>param.frac_slow)
		self.ia_time = ia_time
		self.pending_TXN = {}
		self.peers = {}

		# Bloackchain stores a list of blocks
		# Key is the uniqueID of the block
		# Value is a listof two elements:
		# First is the distance from genesis block
		# Second is the pointer to the block object for the block
		self.blockchain = {}
		self.blockchain[0] = [1,genesisBlock()]
		self.longest = self.blockchain[0]

	# Handle to add new peer 
	def add_peer(self,peer):
		self.peers[peer.uniqueID] = [random.uniform(0.001,0.5),param.MB2b*(5+95*(self.fast and peer.fast))]

	# Generate a new transaction
	def generateTransaction(self, payee_ID, amount, start_time):

		# Compute time at which the TXN is generated (using exponetial distribution)
		next_event_time = random.expovariate(1/self.ia_time) + start_time

		# Unique TXN_ID (as random 32bit integer, assuming collision resistance)
		TXN_ID = random.randint(1,param.TXN_ID_size)

		# Add TXN generation to list of tasks
		param.tasks[next_event_time] = "GenerateTXN: " + str(TXN_ID) + ": " + str(self.uniqueID) + " pays " + str(payee_ID) + " "+str(amount)+" coins"
		
		# Update own set of pending TXN
		self.pending_TXN[TXN_ID] = param.tasks[next_event_time].split(": ",1)[1]

		# Broadcast to peers (omit no peers)
		self.broadcastTransaction(param.tasks[next_event_time].split(": ",1)[1],next_event_time,[])

	# Broadcast the TXN
	# Broadcasts to all the peers if a new TXN is generated
	# If it is forwarded, the sender is omitted
	def broadcastTransaction(self, TXN, start_time, peers_to_omit):
		for peer in self.peers:
			if (peer in peers_to_omit):
				continue
			param.tasks[self.peers[peer][0]+ param.TXN_size/self.peers[peer][1] +\
			 random.expovariate(self.peers[peer][1]/(96*1024)) + start_time]\
			 = "ReceiveTXN: "+str(self.uniqueID)+" "+str(peer)+" " + TXN

	def receiveTransaction(self, TXN, start_time, sender):
		# Proceed to broadcat if TXN not already received
		# Else it would have been broadcasted earlier
		if (int(TXN.split(":")[0]) not in self.pending_TXN):
			self.pending_TXN[int(TXN.split(":")[0])] = TXN
			self.broadcastTransaction( TXN, start_time, sender)

	# Function to generate block
	def generateBlock(self):
		pass
	
	# Function to broadcast a block to peers
	def broadcastBlock(self):
		pass

	# Function to receive block
	# It will also validate the received block and broadcast further if valid
	def receiveBlock(self):
		pass


# Object defining the structure of instance block
# Add other methods/arguments as required
class block:

	def __init__(self, prev_block):
		self.prev_block = prev_block
		self.uniqueID = random.randint(1,param.Block_ID_size)

# Genesis block. All nodes start with this (see init function of node).
class genesisBlock:

	def __init__(self):
		self.uniqueID = 0