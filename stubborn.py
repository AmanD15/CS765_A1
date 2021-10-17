import param
from obj import *

class stubborn(node):
    def __init__(self,uniqueID, t_tx):
        node.__init__(self, uniqueID, t_tx)
        self.fast = 1
        self.private_longest = [0,0]
        self.private_chain = []
        

    # Function to generate block
    def generateBlock(self, start_time):

        # Mine on the longest private chain
        # Hence, the longest private chain block acts as previous block
        new_block = block(self.private_longest[1])
        new_block.creator = self.uniqueID

        # Update longest private chain by adding own block
        self.private_longest = [self.private_longest[0]+1,new_block.uniqueID]

        # Add block to private blockchain maintained by self. 0 -> block, 1 -> creator
        self.private_chain.append(self.private_longest)

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
        new_block.balances_at_end[self.uniqueID] += param.mining_fee
        
    # Function which receives block from honest miners
    def receiveBlock(self,blockID,start_time,sender):
        # Block already received from some source
        if int(blockID) in self.blockchain.keys():
            return
        block = param.blocks[int(blockID)]

        # Code to check whether the block is valid
        if (int(blockID) in self.wait_for_parent):
            block_valid = self.validateBlock(block,1)
        else:
            block_valid = self.validateBlock(block)

        if (block_valid is None):
            param.tasks[param.wait_for_parent + start_time] \
                = "ReceiveBlock: " + str(sender[0]) + " " + str(self.uniqueID) + " " + str(blockID)

        # Proceed if block is valid
        # Else, do nothing
        if (block_valid):

            # Calculate previous lead of attacker
            difference = self.private_longest[0] - self.longest[0]

            # Add block to own blockchain
            self.addBlockToBlockchain(block)

            # If tie and honest mine a block, attacker loses and starts over again
            if difference == 0:
                self.private_chain = []
                param.tasks.pop(self.timeNextBlock)
                self.generateBlockEvent(start_time)                

            # Else the miner releases all the blocks
            else:
                self.broadcastBlock(self.private_chain[0][1],start_time,[])
                self.balance += param.mining_fee
                self.blockchain[self.private_chain[0][1]] = self.private_chain[0]
                released_blk = self.private_chain.pop(0)
                self.longest = released_blk

    # Add block to the local blockchain
    def addBlockToBlockchain(self,block):
        prev_blockID = block.prev_blockID
        length = self.blockchain[prev_blockID][0]+1
        self.blockchain[block.uniqueID] = [length,block.uniqueID]
        #  Update longest if the added block forms the longest chain
        if (length > self.private_longest[0]):
            self.longest = [length,block.uniqueID]
            self.private_longest = [length,block.uniqueID]

    def computeMDU(self):
        num_blocks_self = 0
        last_seen = self.longest[1]
        while (last_seen != 0):
            last_block = param.blocks[last_seen]
            if (last_block.creator == self.uniqueID):
                num_blocks_self += 1
            last_seen = last_block.prev_blockID

        total_blocks = len(self.blockchain)
        total_in_chain = self.longest[0]
        return [num_blocks_self,total_in_chain,total_blocks]
