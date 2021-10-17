import func
import param
from obj import node

# Parse the user inputs
func.parseInputs()

# generate nodes and fully connected P2P network
func.createNetwork()


class selfish(node):
    def __init__(self):


    def computeLeadState(self,has_attacker_generated):
        if (self.private[0] - self.longest[0])>=2:
            return str(self.private[0] - self.longest[0])
        if (has_attacker_generated and (self.private[0] - self.longest[0])==1):
            return "1"
        if ((not has_attacker_generated) and (self.private[0] - self.longest[0])==1):
            return "0'"
        return "0"