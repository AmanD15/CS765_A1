import func
import param
import random

# Parse command line inputs
func.parseInputs()

# Generate the nodes and create a P2P network
func.createNetwork()

# Simulator
func.simulate()

# Write back to file for visualisation
for nodes in param.nodes.values():
    nodes.writeDataToFile()