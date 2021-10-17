import param
from obj import node, block

class selfish(node):
    def __init__(self):
        self.private_longest = [0, 0]
        self.private_chain = []
        self.fast = 1
        self.difference = 0
        self.private_branch_length = 0
        self.chain_length = 0

    # Generate block event
    def generateBlockEvent(self,start_time):
        # Compute time at which the block is generated (using exponetial distribution)
        next_event_time = random.expovariate(1 / self.t_k) + start_time

        # Add TXN generation to list of tasks
        param.tasks[next_event_time] = "GeneratePrivateBlock: " + str(self.uniqueID)
        self.timeNextBlock = next_event_time

    # Function to generate block
    def generateBlock(self, start_time):
        # Update difference
        self.difference = self.private_branch_length - self.chain_length

        # Mine on the longest private chain
        # Hence, the longest private chain block acts as previous block
        new_block = block(self.private_longest[1])
        new_block.creator = self.uniqueID

        # Update longest private chain by adding own block
        self.private_longest = [self.private_longest[0]+1,new_block.uniqueID]

        # Add block to private blockchain maintained by self. 0 -> block, 1 -> creator
        self.private_chain.append([new_block, self.private_chain[-1][0].uniqueID])

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

        # Update the length of private branch
        self.private_branch_length += 1

        # Start mining on the private chain
        self.generateBlockEvent(start_time)

    def broadcastChain(self, start_time, num_blocks = "all"):
        # Case when lead is 2 and honest mine a block
        if num_blocks == "all":
            chain = self.private_chain
        # Case when lead > 2 and honest mine a block
        else:
            chain = self.private_chain[0]

        # Iterate over all the blocks in the private chain
        for blocks, uniqueIDs in chain:
            # Update in global tasks the event for reception by peer
            # based on delays
            blockID = uniqueIDs
            param.tasks[self.peers[peer][0] + param.blocks[blockID].size / self.peers[peer][1] + \
                        random.expovariate(self.peers[peer][1] / (96 * 1024)) + start_time] \
                = "ReceivePrivateBlock: " + str(self.uniqueID) + " " + str(peer) + " " + str(blockID)

        # Since the private chain has been broadcast, intialise it to empty
        self.private_chain = []

    # Function which receives block from honest miners
    def receiveBlockSelfish(self,blockID,start_time):
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

            # Calculate previous lead of attacker
            self.difference = self.private_branch_length - self.chain_length

            # If tie and honest mine a block, attacker loses and starts over again
            if self.difference == 0:
                self.private_chain = []
                self.private_branch_length = 0
                self.chain_length = 0

            # If previous lead is 1 or 2 and honest mine a block -> attacker releases chain
            elif self.difference == 1 or self.difference == 2:
                self.broadcastChain(start_time)
                self.private_chain = []
                self.private_branch_length = 0
                self.chain_length = 0

            # If previous lead is > 2 and honest mine a block -> attacker releases one block from private chain
            else:
                self.broadcastChain(start_time, "one")
                self.private_chain.pop(0)
                self.private_branch_length -= 1
                self.chain_length = 0

    # Function which receives block from honest miners
    def receiveBlockStubborn(self,blockID,start_time):
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

            # Calculate previous lead of attacker
            self.difference = self.private_branch_length - self.chain_length

            # If tie and honest mine a block, attacker loses and starts over again
            if self.difference == 0:
                self.private_chain = []
                self.private_branch_length = 0
                self.chain_length = 0

            # If previous lead is 1 and honest mine a block -> attacker releases chain
            elif self.difference == 1:
                self.broadcastChain(start_time)
                self.private_chain = []
                self.private_branch_length = 0
                self.chain_length = 0

            # If previous lead is >= 2 and honest mine a block -> attacker releases one block from private chain
            else:
                self.broadcastChain(start_time, "one")
                self.private_chain.pop(0)
                self.private_branch_length -= 1
                self.chain_length = 0
