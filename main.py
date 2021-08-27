import obj
import func
import param
import random

# Creates nodes
nodes = func.createNodes()

# Randomly samples nodes to connect peers
func.connectPeers()

# Generate first empty transaction for each node
for i in range(param.num_nodes):
    param.nodes[i].generateTransaction(i,0,0)

# Simulator
# Simulate till there are no pending tasks left
while len(param.tasks.keys()):

    # Read the next task to perform
    task = sorted(param.tasks.keys())[0]

    # Print the next task (Debugging)
    print("Time  ",task,"\t",param.tasks[task])

    # Generate new transaction after the current one is broadcasted
    if param.tasks[task].split(":")[0] == "GenerateTXN":
        nodeID = int(param.tasks[task].split(" ")[2])
        node = param.nodes[nodeID]
        node.balance -= int(param.tasks[task].split(" ")[5])

        # Dummy transaction to maintain interarrival times if balance is zero
        if (node.balance < 1):
            node.generateTransaction(nodeID,0,task)
        
        # Next transaction
        else:
            node_to_pay = random.randint(0,param.num_nodes-1)
            if (node_to_pay == nodeID):
                node.generateTransaction(node_to_pay,0,task)
            else:
                amount_to_pay = random.randint(1,node.balance)
                node.generateTransaction(node_to_pay,amount_to_pay,task)

    # Handle reception of transactions
    if param.tasks[task].split(":")[0] == "ReceiveTXN":
        data = param.tasks[task].split(" ",3)
        param.nodes[int(data[2])].receiveTransaction(data[3],task,[int(data[1])])

    money_in_circulation = 0
    for node in param.nodes.values():
        money_in_circulation += node.balance
    # print(money_in_circulation)


    # Delete the task after it is processed appropriately
    del param.tasks[task]