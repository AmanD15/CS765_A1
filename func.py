import obj
import param
import random

# Creates nodes in the network
def createNetwork():
    for i in range(param.num_nodes):
        param.nodes[i] = (obj.node(i,20))

    # Generate a connected graph through random sampling
    for i in range(len(param.nodes)):
        first_peer = random.randint(0,len(param.nodes)-1)
        if (first_peer == i):
            first_peer = 0
            if (i==0) and len(param.nodes)>1:
                first_peer = 1
        param.nodes[i].add_peer(param.nodes[first_peer])
        param.nodes[first_peer].add_peer(param.nodes[i])
        for j in range(i+1,len(param.nodes)):
            if (random.random()<param.uniform_sampling_p):
                param.nodes[i].add_peer(param.nodes[j])
                param.nodes[j].add_peer(param.nodes[i])