import func
import param
import random


args = func.parseInputs()
func.createNetwork()

# Simulator
func.simulate()

# Write back to file for visualisation
for nodes in param.nodes.values():
    nodes.writeDataToFile()

# for block in param.blocks.values():
#     print(block.uniqueID,block.creator)