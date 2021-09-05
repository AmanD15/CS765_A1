import param
import random

# Formats used for storing different tasks
# Transaction: <Payer> pays <Payee> <Amount> coins
# GenerateTXN: <TXN_generating_node>
# ReceiveTXN: <sender> <receiver> <TXN_ID>
# GenerateBlock: <Creator> <Block_ID>
# ReceiveBlock: <sender> <receiver> <Block_ID>


# Node class to store each peer
class node:

    # Initialize
    def __init__(self, uniqueID, t_tx):
        self.uniqueID = uniqueID
        self.fast = (random.random() > param.percent_slow)
        self.t_tx = t_tx
        self.t_k = param.T_k
        self.pending_TXN = set()
        self.peers = {}
        self.balance = param.start_coins
        self.perceived_balance = {}

        # Blockchain stores a list of blocks validated by the node
        # Key is the uniqueID of the block
        # Value is a list of two elements:
        # First is the distance from genesis block
        # Second is the pointer to the block object for the block
        # As the block has the ID of the previous block, we can create a chain from the block
        self.blockchain = {}
        self.blockchain[0] = [0, genesisBlock()]
        self.longest = self.blockchain[0]
        self.timeNextBlock = 0

    # Handle to add new peer
    def add_peer(self, peer):
        self.peers[peer.uniqueID] = [random.uniform(0.001, 0.5), param.MB2b * (5 + 95 * (self.fast and peer.fast))]

    # Generate transaction event
    def generateTransactionEvent(self,start_time):
        # Compute time at which the TXN is generated (using exponetial distribution)
        next_event_time = random.expovariate(1 / self.t_tx) + start_time
        
        # Add TXN generation to list of tasks
        param.tasks[next_event_time] = "GenerateTXN: " + str(self.uniqueID)

    # Generate a new transaction when the simulator sees the TXN event
    def generateTransaction(self, payee_ID, amount, start_time):

        # Unique TXN_ID
        TXN_ID = param.next_TXN_ID
        param.next_TXN_ID += 1

        # Update own set of pending TXN
        self.pending_TXN.add(TXN_ID)

        # Update global list of transactions
        param.transactions[TXN_ID] = Transaction(TXN_ID,self.uniqueID,payee_ID,amount)
        print("\t\t\t\t",param.transactions[TXN_ID].printTransaction())

        # Update current balance
        self.balance -= amount

        # Broadcast to peers (omit no peers)
        self.broadcastTransaction(TXN_ID, start_time, [])

    # Broadcast the TXN
    # Broadcasts to all the peers if a new TXN is generated
    # If it is forwarded, the sender is omitted
    def broadcastTransaction(self, TXN_ID, start_time, peers_to_omit):
        for peer in self.peers:
            if (peer in peers_to_omit):
                continue
            param.tasks[self.peers[peer][0] + param.TXN_size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveTXN: " + str(self.uniqueID) + " " + str(peer) + " " + str(TXN_ID)

    def receiveTransaction(self, TXN_ID, start_time, sender):

        # Proceed to broadcast if TXN not already received
        # Else it would have been broadcasted earlier
        TXN_ID = int(TXN_ID)
        if (TXN_ID not in self.pending_TXN):
            self.pending_TXN.add(TXN_ID)
            self.broadcastTransaction(TXN_ID, start_time, sender)

            # Check whether the money in the TXN is for the receiver
            if (param.transactions[TXN_ID].payee - self.uniqueID == 0):
                self.balance += param.transactions[TXN_ID].amount


    # Generate block event
    def generateBlockEvent(self,start_time):
        # Compute time at which the block is generated (using exponetial distribution)
        next_event_time = random.expovariate(1 / self.t_k) + start_time

        # Add TXN generation to list of tasks
        param.tasks[next_event_time] = "GenerateBlock: " + str(self.uniqueID) + " " + str(new_block.uniqueID)
        self.timeNextBlock = next_event_time
    
    # Function to generate block
    def generateBlock(self, start_time):
        new_block = block(self.longest[1])
        self.longest = [self.longest[0]+1,new_block]
        self.blockchain[new_block.uniqueID] = self.longest
        param.blocks[new_block.uniqueID] = new_block

        # Add transactions to block
        i = 0

        #  Coinbase TXN
        TXN_ID = param.next_TXN_ID
        param.next_TXN_ID += 1
        block.append(Transaction(TXN_ID,-1,self.uniqueID,param.mining_fee))
        # Other transactions
        for TXN in self.pending_TXN:
            if (i < 1023):
                new.block.transactions.add(TXN)
                self.pending_TXN.remove(TXN)
        new_block.size = param.TXN_size * len(new_block.transactions)

        # Add mining fee to balance
        self.balance += param.mining_fee

        # Broadcast to peers (omit no peers)
        self.broadcastBlock(new_block, next_event_time, [])

    # Function to broadcast a block to peers
    def broadcastBlock(self, block, start_time, peers_to_omit):
        for peer in self.peers:
            if (peer in peers_to_omit):
                continue
            param.tasks[self.peers[peer][0] + block.size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveBlock: " + str(self.uniqueID) + " " + str(peer) + " " + str(block.uniqueID)

    # Function to receive block
    # It will also validate the received block and broadcast further if valid
    def receiveBlock(self,blockID,start_time,sender):
        block = param.blocks[blockID]
        block_valid = 1
        
        # Code to check whether the block is valid
        

        # Proceed if block is valid
        # Else, do nothing
        if (block_valid):
            self.addBlockToBlockchain(blockID)
            self.broadcastBlock(blockID, start_time, sender)
            param.tasks.pop(self.timeNextBlock)
            self.generateBlockEvent(start_time)
            
    def addBlockToBlockchain(BlockID):
        block = param.blocks[BlockID]
        prev_block = block.prev_block
        length = blockchain[prev_block][0]+1
        if (length > self.longest[0]):
            self.longest = [length,block]
			
    def writeDataToFile(self):
        file = open(param.file_prefix + str(self.uniqueID) + param.file_extension, "w")
        for block in self.blockchain.values():
            if (block[1].uniqueID == 0):
                continue
            else:
                file.write(str(block[1].uniqueID) + " " + str(block[1].prev_block.uniqueID) + "\n")
        file.close()


class Transaction:

    def __init__(self,uniqueID,payer,payee,amount):
        self.uniqueID = uniqueID
        # Put payer = -1 for coinbase TXN
        self.payer = payer
        self.payee = payee
        self.amount = amount
    
    def printTransaction(self):
        return ( str(self.uniqueID) + ": " + str(self.payer) + " pays " + str(self.payee) + " " + str(self.amount) + " coins")

# Object defining the structure of instance block
# Add other methods/arguments as required
class block:

    def __init__(self, prev_block):
        self.prev_block = prev_block
        self.size = 0
        self.uniqueID = param.next_block_ID
        param.next_block_ID += 1
        self.transactions = []


# Genesis block. All nodes start with this (see init function of node).
class genesisBlock:

    def __init__(self):
        self.uniqueID = 0
        self.size = param.TXN_size
