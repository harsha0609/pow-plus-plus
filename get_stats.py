import json
import csv
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

# Write to CSV file
csv_file = 'miner_rewards_blocks.csv'
fieldnames = ["Miner ID", "Reward", "Blocks Added"]

with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for miner_id in range(5000, 5050):
        miner_str = str(miner_id)
        writer.writerow({
            "Miner ID": miner_str,
            "Reward": miner_rewards[miner_str],
            "Blocks Added": miner_blocks_added[miner_str]
        })

print(f"CSV file '{csv_file}' has been successfully created with miner rewards and blocks added.")
