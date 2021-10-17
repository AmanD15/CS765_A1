import param
from obj import *

class selfish(node):
    def __init__(self, uniqueID, t_tx):
        node.__init__(self, uniqueID, t_tx)
        self.private = self.longest
        self.private_chain = []

    def computeLeadState(self):
        if (self.private[0] - self.longest[0])>=2:
            return str(self.private[0] - self.longest[0] - 1)
        if (self.private[0] - self.longest[0]==1):
            return "0'"
        return "0"

    def generateBlock(self,start_time):
        # Mine on the private chain
        new_block = block(self.private[1])
        new_block.creator = self.uniqueID
        # Update private chain by adding own block
        self.private = [self.private[0]+1,new_block.uniqueID]
        # Add block to blockchain maintained by self
        self.private_chain.append(self.private)
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
        # self.balance += param.mining_fee

        # Broadcast to peers (omit no peers)
        self.broadcastBlock(new_block.uniqueID, start_time, [])

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

            state = self.computeLeadState()
            if (state != "0" and len(self.private_chain) >0):
                self.balance += 50
                self.broadcastBlock(self.private_chain[0][1],start_time,[])
                blk = self.private_chain.pop(0)
                self.blockchain[blk[1]] = blk
         
            # When in state 0
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
        if (length > self.private[0]):
            self.longest = [length,block.uniqueID]
