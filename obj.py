import param
import random


# Node class to store each peer
class node:

    # Initialize
    def __init__(self, uniqueID, ia_time):
        self.uniqueID = uniqueID
        self.fast = (random.random() > param.percent_slow)
        self.ia_time = ia_time
        self.pending_TXN = {}
        self.peers = {}
        self.balance = 0

        # Blockchain stores a list of blocks validated by the node
        # Key is the uniqueID of the block
        # Value is a list of two elements:
        # First is the distance from genesis block
        # Second is the pointer to the block object for the block
        # As the block has the ID of the previous block, we can create a chain from the block
        self.blockchain = {}
        self.blockchain[0] = [0, genesisBlock()]
        self.longest = self.blockchain[0]

    # Handle to add new peer
    def add_peer(self, peer):
        self.peers[peer.uniqueID] = [random.uniform(0.001, 0.5), param.MB2b * (5 + 95 * (self.fast and peer.fast))]

    # Generate a new transaction
    def generateTransaction(self, payee_ID, amount, start_time):

        # Compute time at which the TXN is generated (using exponetial distribution)
        next_event_time = random.expovariate(1 / self.ia_time) + start_time

        # Unique TXN_ID
        TXN_ID = param.next_TXN_ID
        param.next_TXN_ID += 1

        # Add TXN generation to list of tasks
        param.tasks[next_event_time] = str(TXN_ID) + ": " + str(self.uniqueID) + " pays " + str(payee_ID) \
                                       + " " + str(amount) + " coins"

        # Update own set of pending TXN
        self.pending_TXN[TXN_ID] = param.tasks[next_event_time].split(": ", 1)[1]

        # Broadcast to peers (omit no peers)
        self.broadcastTransaction(param.tasks[next_event_time].split(": ", 1)[1], next_event_time, [])

    # Broadcast the TXN
    # Broadcasts to all the peers if a new TXN is generated
    # If it is forwarded, the sender is omitted
    def broadcastTransaction(self, TXN, start_time, peers_to_omit):
        for peer in self.peers:
            if (peer in peers_to_omit):
                continue
            param.tasks[self.peers[peer][0] + param.TXN_size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveTXN: " + str(self.uniqueID) + " " + str(peer) + " " + TXN

    def receiveTransaction(self, TXN, start_time, sender):

        # Proceed to broadcast if TXN not already received
        # Else it would have been broadcasted earlier
        if (int(TXN.split(":")[0]) not in self.pending_TXN):
            self.pending_TXN[int(TXN.split(":")[0])] = TXN
            self.broadcastTransaction(TXN, start_time, sender)

            # Check whether the money in the TXN is for the receiver
            if (int(TXN.split(" ")[3]) - self.uniqueID == 0):
                self.balance += int(TXN.split(" ")[4])

    # Function to generate block
    def generateBlock(self, start_time):
        # Compute time at which the TXN is generated (using exponetial distribution)
        # Copied from TXN part.  Edit mean creation time as suitable
        next_event_time = random.expovariate(1 / self.ia_time) + start_time

        new_block = block(self.longest[1])
        param.blocks[new_block.uniqueID] = new_block

        # Add TXN generation to list of tasks
        param.tasks[next_event_time] = "GenerateBlock: " + str(self.uniqueID) + " " + str(new_block.uniqueID)

        # Broadcast to peers (omit no peers)
        self.broadcastBlock(new_block, next_event_time, [])

    # Function to broadcast a block to peers
    def broadcastBlock(self, block, start_time, peers_to_omit):
        for peer in self.peers:
            if (peer in peers_to_omit):
                continue
            param.tasks[self.peers[peer][0] + param.Block_size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceiveBlock: " + str(self.uniqueID) + " " + str(peer) + " " + str(block.uniqueID)

    # Function to receive block
    # It will also validate the received block and broadcast further if valid
    def receiveBlock(self):
        pass

    def writeDataToFile(self):
        file = open(param.file_prefix + str(self.uniqueID) + param.file_extension, "w")
        for block in self.blockchain.values():
            if (block[1].uniqueID == 0):
                continue
            else:
                file.write(str(block[1].uniqueID) + " " + str(block[1].prev_block.uniqueID) + "\n")
        file.close()


# Object defining the structure of instance block
# Add other methods/arguments as required
class block:

    def __init__(self, prev_block):
        self.prev_block = prev_block
        self.uniqueID = param.next_block_ID
        param.next_block_ID += 1


# Genesis block. All nodes start with this (see init function of node).
class genesisBlock:

    def __init__(self):
        self.uniqueID = 0
