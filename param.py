max_sim_time = 100

not_included_TXN = 5

num_nodes = 50
num_connections = 12
start_coins = 0.0

T_tx = 10
T_k = 50

mining_fee = 50

percent_slow = 0.2

TXN_size = 1024 * 8			# 1kB
MB2b = 1024 * 1024 * 8		# Convert MB to bits

# Dictionary storing global pending tasks
# To be used by the simulator to jump to the next event
# Key is the time at which event occurs
# Value is a string describing the event
tasks = {}

nodes = {}
blocks = {}
transactions = {}

next_TXN_ID = 0
next_block_ID = 1

file_prefix = "bin/Blockdata_node_"
file_prefix2 = "bin/Data"
file_extension = ".txt"