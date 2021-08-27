num_nodes = 100

uniform_sampling_p = 0.1

frac_slow = 0.5             # Fraction of slow nodes
TXN_size = 1024 * 8			# 1kB
MB2b = 1024 * 1024 * 8		# Convert MB to bits

block_ID_size = 0x11111111	# 32 bit ID for blocks
TXN_ID_size = 0x11111111	# 32 bit ID for TXN

# Dictionary storing global pending tasks
# To be used by the simulator to jump to the next event
# Key is the time at which event occurs
# Value is a string describing the event
tasks = {}
nodes = {}

next_TXN_ID = 0
next_block_ID = 1