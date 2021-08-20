import obj
import random

new_block = obj.genesisBlock()
node = []
for i in range(10):
    node.append(obj.node(i,0.1))
for i in range(10):
    node[i].add_peer(node[random.randint(0,9)])
    TXN = node[i].generateTransaction(9-i,random.randint(0,9))


for task in sorted(obj.tasks):
    print(obj.tasks[task])