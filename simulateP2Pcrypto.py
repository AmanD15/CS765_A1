import func
import param

# Parse command line inputs
func.parseInputs()

# Generate the nodes and create a P2P network
func.createNetwork()

# Simulator
func.simulate()

# Write back to file for visualisation
for nodes in param.nodes.values():
    nodes.writeDataToFile()

file = open(param.file_prefix2 + param.file_extension, "a")
file.write("Total blocks:"+str(len(param.blocks))+str("\n\n"))
file.close()