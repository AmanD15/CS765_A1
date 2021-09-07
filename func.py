# The file contains different global functions needed for the execution of script

from obj import node, genesisBlock
import param
import random
import numpy as np
import argparse
import os

# Parse the input arguments using argparse
def parseInputs():
    parser = argparse.ArgumentParser(description="Simulate a P2P network")
    parser.add_argument('--num_nodes', type=int, default = 10, help = "Number of nodes in the P2P network")
    parser.add_argument('--percent_slow', type=float, default = 0.5, help = "Percentage of slow nodes in the network")
    parser.add_argument('--T_tx', type=float, default = 10, help = "Mean of interarrival times of transactions on node")
    parser.add_argument('--T_k', type=float, default = 50, help = "Mean of random variable generated by node during PoW")
    parser.add_argument('--start_coins', type=float, default=0.0, help="Number of coins each peer has at"
                                                                         " the beginning, default = 0")
    parser.add_argument('--simT', type=float, default = 100, help = "Maximum simulation time for which the simulator should be run")


    args = parser.parse_args()

    # Store the input arguments into parameters file
    param.num_nodes = args.num_nodes
    param.percent_slow = args.percent_slow
    param.T_tx = args.T_tx
    param.T_k = args.T_k
    param.start_coins = args.start_coins
    param.max_sim_time = args.simT
    # Create file for data
    file = open(param.file_prefix2 + param.file_extension, "w")
    file.close()

    return args


# Creates nodes in the network
def createNetwork():

    num_nodes = param.num_nodes
    num_connections = param.num_connections

    # Create new nodes and add to global list of nodes
    for i in range(num_nodes):
        # Node ID = i, interarrival time = T_tx
        param.nodes[i] = node(i,param.T_tx)

    # We first create a minimum spanning tree by just performing a random walk on the nodes
    shuffled_indices = list(range(num_nodes))
    random.shuffle(shuffled_indices)    # Shuffle node indices

    adjacency_matrix = np.zeros((num_nodes, num_nodes))

    np.fill_diagonal(adjacency_matrix, 1)

    # Iterate over all the node indices
    for index in range(num_nodes - 1):
        param.nodes[shuffled_indices[index]].add_peer(param.nodes[shuffled_indices[index+1]]) # Add two consecutive nodes as
        param.nodes[shuffled_indices[index+1]].add_peer(param.nodes[shuffled_indices[index]]) # neighbours according to shuffling
        adjacency_matrix[shuffled_indices[index], shuffled_indices[index+1]] = 1    # Update edges in adjacency matrix
        adjacency_matrix[shuffled_indices[index+1], shuffled_indices[index]] = 1

    # These many edges are still left to be assigned
    num_connections_left = num_connections - num_nodes + 1

    while num_connections_left > 0:  # Till all edges havent been assigned
        no_connection_rows, no_connection_cols = np.where(adjacency_matrix == 0)   # Edges that dont exist in the network
        random_edge = random.choice(range(len(no_connection_rows)))
        param.nodes[no_connection_rows[random_edge]].add_peer(param.nodes[no_connection_cols[random_edge]])
        param.nodes[no_connection_cols[random_edge]].add_peer(param.nodes[no_connection_rows[random_edge]])
        adjacency_matrix[no_connection_cols[random_edge], no_connection_rows[random_edge]] = 1
        adjacency_matrix[no_connection_rows[random_edge], no_connection_cols[random_edge]] = 1

        num_connections_left = num_connections_left - 1


# Simulate till there are no pending tasks left
def simulate():

    # Create genesis block
    param.blocks[0] = genesisBlock()

    # Initialization for each node
    for i in range(param.num_nodes):
        # Generate first empty transaction
        param.nodes[i].generateTransactionEvent(0)
        # Start mining on all nodes
        param.nodes[i].generateBlockEvent(0)

    # Till there are events to be processed by the simulator
    while len(param.tasks.keys()):

        # Jump to the next task to perform
        next_event_time = min(param.tasks.keys())
        # Return if max simulation time exceeded
        if next_event_time > param.max_sim_time:
            break

        # Print the task
        # print("Time  ",next_event_time,"\t",param.tasks[next_event_time])


        # Handle generation of TXN by a node
        # Format - GenerateTXN: <TXN_generating_node>
        if param.tasks[next_event_time].split(":")[0] == "GenerateTXN":
            node = param.nodes[int(param.tasks[next_event_time].split(" ")[1])]

            # Dummy transaction to self to maintain interarrival times, if balance is zero
            if node.balance < 1:
                node.generateTransaction(node.uniqueID,0,next_event_time)
            
            # Execute transaction
            else:
                node_to_pay = random.randint(0, param.num_nodes-1)
                if node_to_pay == node.uniqueID:
                    node.generateTransaction(node_to_pay,0,next_event_time)
                else:
                    amount_to_pay = random.randint(1,node.balance)
                    node.generateTransaction(node_to_pay,amount_to_pay,next_event_time)

            # Generate next transaction event after the current one is broadcasted
            node.generateTransactionEvent(next_event_time)



        # Handle reception of transactions
        # Format - ReceiveTXN: <sender> <receiver> <TXN_ID>
        if param.tasks[next_event_time].split(":")[0] == "ReceiveTXN":
            data = param.tasks[next_event_time].split(" ",3)
            param.nodes[int(data[2])].receiveTransaction(data[3],next_event_time,[int(data[1])])



        # Handle generate of new blocks
        # Format - GenerateBlock: <Creator>
        if param.tasks[next_event_time].split(":")[0] == "GenerateBlock":
            node = param.nodes[int(param.tasks[next_event_time].split(" ")[1])]

            node.generateBlock(next_event_time)
            
            # Generate next block event
            node.generateBlockEvent(next_event_time)



        # Handle reception of blocks from peers
        # Format - ReceiveBlock: <sender> <receiver> <Block_ID>
        if param.tasks[next_event_time].split(":")[0] == "ReceiveBlock":
            data = param.tasks[next_event_time].split(" ",3)
            param.nodes[int(data[2])].receiveBlock(data[3],next_event_time,[int(data[1])])


        # Compute total money in circulation
        money_in_circulation = 0
        for node in param.nodes.values():
            money_in_circulation += node.balance
        # print("Time  ",next_event_time,"\t Money in circulation =",money_in_circulation,"coins")

        # Remove the task from the simulator queue it is processed appropriately
        del param.tasks[next_event_time]