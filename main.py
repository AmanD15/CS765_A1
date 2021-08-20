import obj
import random
import func
new_block = obj.genesisBlock()

num_nodes = 10
nodes = func.createNodes(num_nodes)
func.connectPeers(nodes)

for i in range(num_nodes):
    TXN = nodes[i].generateTransaction(num_nodes - i - 1,random.randint(0,num_nodes-1))

while len(obj.tasks.keys()):
    task = sorted(obj.tasks.keys())[0]
    print(obj.tasks[task])
    if obj.tasks[task].split(":")[0] == "ReceiveTXN":
        nodes[int(obj.tasks[task].split(" ")[1])].receiveTransaction(obj.tasks[task].split(" ",2)[2],task)
    del obj.tasks[task]