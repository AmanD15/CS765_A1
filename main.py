import obj
import func
import param
import random

# Creates nodes
nodes = func.createNodes(param.num_nodes)

# Randomly samples nodes to connect peers
func.connectPeers()

# Generate one transaction for each node
for i in range(param.num_nodes):
    param.nodes[i].generateTransaction(param.num_nodes - i - 1,random.randint(0,10),0)

# Simulator
# Simulate till there are pending tasks left
while len(param.tasks.keys()):

    # Read the next task to perform
    task = sorted(param.tasks.keys())[0]

    # Print the next task (Debugging)
    print("Time  ",task,"\t",param.tasks[task])

    # Handle reception of transactions
    if param.tasks[task].split(":")[0] == "ReceiveTXN":
        param.nodes[int(param.tasks[task].split(" ")[2])].\
        receiveTransaction(param.tasks[task].split(" ",3)[3],\
        task,\
        [int(param.tasks[task].split(" ")[1])])


    # Delete the task after it is processed appropriately
    del param.tasks[task]