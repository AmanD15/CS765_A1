from obj import node
import param
import random
import numpy as np


# Creates nodes in the network
def createNetwork(num_nodes=10, num_connections=12):

    for i in range(num_nodes):
        param.nodes[i] = node(i,20)

    # We first create a minimum spanning tree by just performing a random walk on the nodes
    shuffled_indices = range(num_nodes)
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

    return adjacency_matrix