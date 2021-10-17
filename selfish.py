import func
import param
from obj import node

# Parse the user inputs
func.parseInputs()

# generate nodes and fully connected P2P network
func.createNetwork()


class selfish(node):
    def __init__(self):
