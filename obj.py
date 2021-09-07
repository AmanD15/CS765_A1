import param
import random

# Transaction format
# Transaction: <Payer> pays <Payee> <Amount> coins

# Formats used for storing different tasks
# GenerateTXN: <TXN_generating_node>
# ReceiveTXN: <sender> <receiver> <TXN_ID>
# GenerateBlock: <Creator>
# ReceiveBlock: <sender> <receiver> <Block_ID>

# Node class to store each peer
class node:

    # Initialize
    def __init__(self, uniqueID, t_tx):
        # UniqueID
        self.uniqueID = uniqueID
        # Tyot - fast or slow
        self.fast = (random.random() > param.percent_slow)
        # Interarrival time
        self.t_tx = t_tx
        # Interarrival time b/w blocks (= inverse of hashing power)
        self.t_k = random.expovariate(1/param.T_k)
        # Update total hashing power in system y adding node's hash power 
        param.total_hash_power += 1/self.t_k
        # List of pending TXN
        self.pending_TXN = []
        # List of peers directly connected
        self.peers = {}
        # Initial balance
        self.balance = param.start_coins

        # Blockchain stores a list of blocks validated by the node
        # Key is the uniqueID of the block
        # Value is a list of two elements:
        # First is the distance from genesis block
        # Second is the pointer to the block object for the block
        # As the block has the ID of the previous block, we can create a chain from the block
        self.blockchain = {}
        self.blockchain[0] = [0, 0]
        # Longest chain encountered so far
        self.longest = self.blockchain[0]
        # Number of blocks created by node
        self.num_blocks_created = 0

        # Time at which next block generation event is scheduled
        self.timeNextBlock = 0

    # Handle to add new peer
    # Each peer data is a list of two elements:
    # The first correspond to \rho_i_j, speed of light propagation delay (asymmetric)
    # The second corresponds to c_i_j, Link speed
    def add_peer(self, peer):
        self.peers[peer.uniqueID] = [random.uniform(0.01, 0.5), param.MB2b * (5 + 95 * (self.fast and peer.fast))]

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
        self.pending_TXN.append(TXN_ID)

        # Update global list of transactions
        param.transactions[TXN_ID] = Transaction(TXN_ID,self.uniqueID,payee_ID,amount)
        # print("\t Transaction \t\t",param.transactions[TXN_ID].printTransaction())

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
            # Update in global tasks the event for reception by peer
            # based on delays
            param.tasks[self.peers[peer][0] + param.TXN_size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveTXN: " + str(self.uniqueID) + " " + str(peer) + " " + str(TXN_ID)

    def receiveTransaction(self, TXN_ID, start_time, sender):

        # Proceed to broadcast if TXN not already received
        # Else it would have been broadcasted earlier
        # And hence no further action required
        TXN_ID = int(TXN_ID)
        if (TXN_ID not in self.pending_TXN):
            self.pending_TXN.append(TXN_ID)
            self.broadcastTransaction(TXN_ID, start_time, sender)

            # Check whether the money in the TXN is for the receiver
            # If yes, update own balance
            if (param.transactions[TXN_ID].payee - self.uniqueID == 0):
                self.balance += param.transactions[TXN_ID].amount


    # Generate block event
    def generateBlockEvent(self,start_time):
        # Compute time at which the block is generated (using exponetial distribution)
        next_event_time = random.expovariate(1 / self.t_k) + start_time

        # Add TXN generation to list of tasks
        param.tasks[next_event_time] = "GenerateBlock: " + str(self.uniqueID)
        self.timeNextBlock = next_event_time
    
    # Function to generate block
    def generateBlock(self, start_time):
        # Mine on the longest chain
        # Hence, the longest chain block acts as previous block
        new_block = block(self.longest[1])
        new_block.creator = self.uniqueID
        # Update longest chain by adding own block
        self.longest = [self.longest[0]+1,new_block.uniqueID]
        # Add block to blockchain maintained by self
        self.blockchain[new_block.uniqueID] = self.longest
        # Add block to global set of blocks
        param.blocks[new_block.uniqueID] = new_block
        # Update number of blocks created
        self.num_blocks_created += 1

        # Add transactions to block
        i = 0

        #  Coinbase TXN
        TXN_ID = param.next_TXN_ID
        param.next_TXN_ID += 1
        coinbase  = Transaction(TXN_ID,-1,self.uniqueID,param.mining_fee)
        param.transactions[TXN_ID] = coinbase
        new_block.transactions.append(TXN_ID)

        # Other transactions
        for TXN in self.pending_TXN:
            # At most 1023 TXn in block, 
            # and not to put most recent TXN due to fear of rejection due to etwork delays
            if ((i >= 1023) or (len(self.pending_TXN) - self.pending_TXN.index(TXN) < param.not_included_TXN)):
                break
            # Ensure positive balance, and no double spend
            if (new_block.balances_at_end[param.transactions[TXN].payer] - param.transactions[TXN].amount >= 0) \
            and (TXN not in new_block.TXN_at_end):
                new_block.transactions.append(TXN)
                new_block.TXN_at_end.add(TXN)
                new_block.balances_at_end[param.transactions[TXN].payer] -= param.transactions[TXN].amount
                new_block.balances_at_end[param.transactions[TXN].payee] += param.transactions[TXN].amount
            i+=1
        # Compute block size
        new_block.size = param.TXN_size * len(new_block.transactions)

        #  Add mining fee to block balances
        new_block.balances_at_end[self.uniqueID] += 50

        # Add mining fee to balance
        self.balance += param.mining_fee

        # Broadcast to peers (omit no peers)
        self.broadcastBlock(new_block.uniqueID, start_time, [])

    # Function to broadcast a block to peers
    # Broadcasts to all the peers if a new block is generated
    # If it is forwarded, the sender is omitted
    def broadcastBlock(self, blockID, start_time, peers_to_omit):
        for peer in self.peers:
            if (peer in peers_to_omit):
                continue
            # Update in global tasks the event for reception by peer
            # based on delays
            param.tasks[self.peers[peer][0] + param.blocks[blockID].size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveBlock: " + str(self.uniqueID) + " " + str(peer) + " " + str(blockID)

    # Function to receive block
    # It will also validate the received block and broadcast further if valid
    def receiveBlock(self,blockID,start_time,sender):
        # Block already received from some source
        if int(blockID) in self.blockchain.keys():
            return
        block = param.blocks[int(blockID)]
        
        # Code to check whether the block is valid
        block_valid = self.validateBlock(block)

        # Proceed if block is valid
        # Else, do nothing
        if (block_valid):

            # Add block to own blockchain
            self.addBlockToBlockchain(block)

            # Broadcast to peers
            self.broadcastBlock(int(blockID), start_time, sender)
            
            # Discard generation of current block if the new block is longest
            # and start mining on the new block
            if (self.longest[1] == param.blocks[int(blockID)]):
                param.tasks.pop(self.timeNextBlock)
                self.generateBlockEvent(start_time)
            
    # Add block to the local blockchain
    def addBlockToBlockchain(self,block):
        prev_blockID = block.prev_blockID
        length = self.blockchain[prev_blockID][0]+1
        self.blockchain[block.uniqueID] = [length,block.uniqueID]
        #  Update longest if the added block forms the longest chain
        if (length > self.longest[0]):
            self.longest = [length,block.uniqueID]

    def validateBlock(self,block):
        # Illegal block - parent was illegal
        if block.prev_blockID not in self.blockchain.keys():
            print("Rejected due to parent not found",block.prev_blockID)
            return 0
        balance = param.blocks[block.prev_blockID].balances_at_end.copy()
        for TXN_ID in block.transactions:
            # Double spend attempt - as TXN already in blockchain
            if (TXN_ID in param.blocks[block.prev_blockID].TXN_at_end):
                print("Rejected due to an attempted double spend")
                return 0
            # TXN not in simulator 
            # (this implies TXN is not received by receiver)
            # will consider it illegal
            if (TXN_ID not in param.transactions.keys()):
                print("Rejected due to illegal TXN")
                return 0
            TXN = param.transactions[TXN_ID]
            if (TXN.payer != -1):
                balance[TXN.payer] -= TXN.amount
                balance[TXN.payee] += TXN.amount
                # TXN not received by receiver from peer- will consider it illegal
                if TXN_ID not in self.pending_TXN:
                    print("Rejected due to illegal TXN")
                    return 0
        # Reject if the balances go negative after the block is generated
        if min(balance.values())<0:
            print("Rejected due to illegal TXN - insufficient balance due to TXN")
            return 0
        # print("Accepted")
        return 1
               

    def writeDataToFile(self):
        file = open(param.file_prefix2 + param.file_extension, "a")
        file.write("ID: "+str(self.uniqueID)+"\n")
        fast = "Slow"
        if (self.fast):
            fast = "Fast"
        file.write("Type: "+fast+"\n")
        file.write("Block generation time: "+str(self.t_k)+"\n")
        file.write("Percentage hashing power: "+str(100/(param.total_hash_power*self.t_k))+"\n")
        file.write("Number of blocks created: "+str(self.num_blocks_created)+"\n")
        num_blocks_in_chain = 0
        blockID = self.longest[1]
        while (blockID != 0):
            if (param.blocks[blockID].creator == self.uniqueID):
                num_blocks_in_chain += 1
            blockID = param.blocks[blockID].prev_blockID
        file.write("Number of blocks in longest chain: "+str(num_blocks_in_chain)+"\n")
        file.write("Length of longest chain: "+str(self.longest[0])+"\n")
        file.write("Balance at end: "+str(param.blocks[self.longest[1]].balances_at_end[self.uniqueID])+"\n\n")
        file.close()

        # Write block data
        # For each node on each line, data format is
        # <BlockID> <Prev_block_ID>
        file = open(param.file_prefix + str(self.uniqueID) + param.file_extension, "w")
        for block in self.blockchain.values():
            if (block[1] == 0):
                continue
            else:
                file.write(str(block[1]) + " " + str(param.blocks[block[1]].prev_blockID) + "\n")
        file.close()


class Transaction:

    def __init__(self,uniqueID,payer,payee,amount):
        self.uniqueID = uniqueID
        # Put payer = -1 for coinbase TXN
        self.payer = payer
        self.payee = payee
        self.amount = amount
    
    def printTransaction(self):
        # Coinbase
        if (self.payer == -1):
            return ( str(self.uniqueID) + ": " + str(self.payee) + " mines " + " " + str(param.mining_fee) + " coins")
        return ( str(self.uniqueID) + ": " + str(self.payer) + " pays " + str(self.payee) + " " + str(self.amount) + " coins")

# Object defining the structure of instance block
# Add other methods/arguments as required
class block:

    def __init__(self, prev_blockID):
        # Previous bloc kID
        self.prev_blockID = prev_blockID
        # Initial size = 0 ; will be updated by generating node before transmission
        self.size = 0
        # Generate unique block ID
        self.uniqueID = param.next_block_ID
        param.next_block_ID += 1
        # Empty list of TXN
        self.transactions = []
        # Unknown miner (updated by miner)
        self.creator = -1
        # Initially inherits balance and TXN from parent node
        # Miners update the chain at the end

        # Note that this data (although storeing history of the chain)
        # is not for miners to directly access.
        # Only miners verifying a block after receiving them use the blockID.
        # The data is to efficiently store the balances at each point in the blockchain
        # to prevent simulator to compute the values everytime a block is received on
        # the non-dominant chain.
        # The direct use by miners is simulation of the computation of all blocks
        # received by miners (which can be readily done as they have access to those blocks).
        self.balances_at_end = param.blocks[prev_blockID].balances_at_end.copy()
        self.TXN_at_end = param.blocks[prev_blockID].TXN_at_end.copy()


# Genesis block. All nodes start with this (see init function of node).
class genesisBlock:

    def __init__(self):
        # Unique ID is 0
        self.uniqueID = 0
        #  Size = size of TXN
        self.size = param.TXN_size
        #  Initialize with no TXN and empty balances
        self.balances_at_end = {}
        self.TXN_at_end = set()
        for node in param.nodes.keys():
            self.balances_at_end[node] = 0
