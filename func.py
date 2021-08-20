import obj
import random

p = 1

def createNodes(num_nodes):
    nodes = []
    for i in range(num_nodes):
        nodes.append(obj.node(i,1))

    return nodes

def connectPeers(nodes):
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            if (random.random()<p):
                nodes[i].add_peer(nodes[j])
                nodes[j].add_peer(nodes[i])