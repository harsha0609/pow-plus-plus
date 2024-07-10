import json
from collections import defaultdict

# Function to calculate rewards and count blocks for each miner
def calculate_rewards_and_blocks(blockchain_data):
    rewards = defaultdict(float)
    blocks_added = defaultdict(int)
    
    # Initialize rewards and blocks added for all miners in the range 5000-5049
    for miner_id in range(5000, 5050):
        rewards[str(miner_id)] = 0.0
        blocks_added[str(miner_id)] = 0
    
    for block in blockchain_data["blockchain"]:
        miner = str(block["miner"])  # Ensure miner ID is treated as string for consistency
        
        # Calculate block reward (assuming fixed 3.125 for each block)
        reward = 3.125
        
        # Add transaction fees
        for transaction in block["transactions"]:
            if "fee" in transaction:
                reward += float(transaction["fee"])
        
        # Accumulate rewards and count blocks for the miner
        rewards[miner] += reward
        blocks_added[miner] += 1
    
    return rewards, blocks_added

# Read JSON data from file
file_path = 'sample_chain.json'  # Adjust path as necessary
with open(file_path, 'r') as file:
    blockchain_data = json.load(file)

# Calculate rewards and count blocks for each miner
miner_rewards, miner_blocks_added = calculate_rewards_and_blocks(blockchain_data)

# Print rewards and number of blocks added for each miner
for miner_id in range(5000, 5050):
    miner_str = str(miner_id)
    reward = miner_rewards[miner_str]
    blocks = miner_blocks_added[miner_str]
    print(f"Miner {miner_str}: Reward {reward}, Blocks Added: {blocks}")
