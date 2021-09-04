import func
import param
import random


args = func.parseInputs()
nodes = func.createNetwork()

# Simulator
func.simulate()

# Write back to file for visualisation
# for nodes in param.nodes.values():
#     nodes.writeDataToFile()