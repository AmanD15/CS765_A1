import param
import random

# Formats used for storing different tasks
# Transaction: <Payer> pays <Payee> <Amount> coins
# GenerateTXN: <TXN_generating_node>
# ReceiveTXN: <sender> <receiver> <TXN_ID>
# GenerateBlock: <Creator>
# ReceiveBlock: <sender> <receiver> <Block_ID>


# Node class to store each peer
class node:

    # Initialize
    def __init__(self, uniqueID, t_tx):
        self.uniqueID = uniqueID
        self.fast = (random.random() > param.percent_slow)
        self.t_tx = t_tx
        self.t_k = param.T_k
        self.pending_TXN = []
        self.peers = {}
        self.balance = param.start_coins
        # self.perceived_balance = {}

        # Blockchain stores a list of blocks validated by the node
        # Key is the uniqueID of the block
        # Value is a list of two elements:
        # First is the distance from genesis block
        # Second is the pointer to the block object for the block
        # As the block has the ID of the previous block, we can create a chain from the block
        self.blockchain = {}
        self.blockchain[0] = [0, 0]
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
            param.tasks[self.peers[peer][0] + param.TXN_size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveTXN: " + str(self.uniqueID) + " " + str(peer) + " " + str(TXN_ID)

    def receiveTransaction(self, TXN_ID, start_time, sender):

        # Proceed to broadcast if TXN not already received
        # Else it would have been broadcasted earlier
        TXN_ID = int(TXN_ID)
        if (TXN_ID not in self.pending_TXN):
            self.pending_TXN.append(TXN_ID)
            self.broadcastTransaction(TXN_ID, start_time, sender)

            # Check whether the money in the TXN is for the receiver
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
        new_block = block(self.longest[1])
        new_block.creator = self.uniqueID
        self.longest = [self.longest[0]+1,new_block.uniqueID]
        self.blockchain[new_block.uniqueID] = self.longest
        param.blocks[new_block.uniqueID] = new_block

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
            if (i >= 1023):
                break
            if (new_block.balances_at_end[param.transactions[TXN].payer] - param.transactions[TXN].amount >= 0) \
            and (TXN not in new_block.TXN_at_end):
                new_block.transactions.append(TXN)
                new_block.TXN_at_end.add(TXN)
                new_block.balances_at_end[param.transactions[TXN].payer] -= param.transactions[TXN].amount
                new_block.balances_at_end[param.transactions[TXN].payee] += param.transactions[TXN].amount
            i+=1
        new_block.size = param.TXN_size * len(new_block.transactions)
        new_block.balances_at_end[self.uniqueID] += 50

        # Add mining fee to balance
        self.balance += param.mining_fee

        # Broadcast to peers (omit no peers)
        self.broadcastBlock(new_block.uniqueID, start_time, [])

    # Function to broadcast a block to peers
    def broadcastBlock(self, blockID, start_time, peers_to_omit):
        for peer in self.peers:
            if (peer in peers_to_omit):
                continue
            param.tasks[self.peers[peer][0] + param.blocks[blockID].size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveBlock: " + str(self.uniqueID) + " " + str(peer) + " " + str(blockID)

    # Function to receive block
    # It will also validate the received block and broadcast further if valid
    def receiveBlock(self,blockID,start_time,sender):
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
            
    def addBlockToBlockchain(self,block):
        prev_blockID = block.prev_blockID
        length = self.blockchain[prev_blockID][0]+1
        self.blockchain[block.uniqueID] = [length,block.uniqueID]
        if (length > self.longest[0]):
            self.longest = [length,block.uniqueID]

    def validateBlock(self,block):
        if block.prev_blockID not in self.blockchain.keys():
            print(block.prev_blockID,"Rejected due to parent not found")
            return 0
        for TXN_ID in block.transactions:
            TXN = param.transactions[TXN_ID]
            if (TXN.payer != -1):
                if TXN_ID not in self.pending_TXN:
                    print("Reject due to illegal TXN")
                    return 0
        print("Accepted")
        return 1
               

    def writeDataToFile(self):
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
        return ( str(self.uniqueID) + ": " + str(self.payer) + " pays " + str(self.payee) + " " + str(self.amount) + " coins")

# Object defining the structure of instance block
# Add other methods/arguments as required
class block:

    def __init__(self, prev_blockID):
        self.prev_blockID = prev_blockID
        self.size = 0
        self.uniqueID = param.next_block_ID
        param.next_block_ID += 1
        self.transactions = []
        self.creator = -1
        self.balances_at_end = param.blocks[prev_blockID].balances_at_end
        self.TXN_at_end = param.blocks[prev_blockID].TXN_at_end


# Genesis block. All nodes start with this (see init function of node).
class genesisBlock:

    def __init__(self):
        self.uniqueID = 0
        self.size = param.TXN_size
        self.balances_at_end = {}
        self.TXN_at_end = set()
        for node in param.nodes.keys():
            self.balances_at_end[node] = 0
