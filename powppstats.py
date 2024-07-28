import json
import csv
from collections import defaultdict

def load_blockchain(filename):
    with open(filename, 'r') as json_file:
        blockchain = json.load(json_file)
    return blockchain

def calculate_statistics(blockchain):
    miner_rewards = defaultdict(float)
    checkpoint_blocks_added = {
        'checkpoint1': defaultdict(int),
        'checkpoint2': defaultdict(int),
        'checkpoint3': defaultdict(int)
    }
    main_blocks_added = defaultdict(int)

    # Define difficulty levels
    difficulty_levels = {
        5: 'checkpoint1',   # Assuming this is the difficulty level for checkpoint1
        10: 'checkpoint2',  # Assuming this is the difficulty level for checkpoint2
        20: 'checkpoint3',  # Assuming this is the difficulty level for checkpoint3
        40: 'main'          # Assuming this is the difficulty level for main blocks
    }

    for block in blockchain:
        if block['index'] == 0:
            continue  # Skip the genesis block

        miner = block['miner']
        transactions = block['transactions']
        difficulty = block['difficulty']
        
        block_type = difficulty_levels.get(difficulty, 'unknown')

        # Calculate rewards from coinbase transactions
        for txn in transactions:
            if txn['from_addr'] is None and txn['to_addr'] == miner:
                miner_rewards[miner] += txn['amount']

        # Count checkpoint and main blocks
        if block_type == 'main':
            main_blocks_added[miner] += 1
        elif block_type in checkpoint_blocks_added:
            checkpoint_blocks_added[block_type][miner] += 1

    return miner_rewards, checkpoint_blocks_added, main_blocks_added

def sort_statistics(miner_rewards, checkpoint_blocks_added, main_blocks_added):
    sorted_miner_rewards = sorted(miner_rewards.items(), key=lambda x: x[1], reverse=True)
    sorted_checkpoint_blocks_added = {
        'checkpoint1': sorted(checkpoint_blocks_added['checkpoint1'].items(), key=lambda x: x[1], reverse=True),
        'checkpoint2': sorted(checkpoint_blocks_added['checkpoint2'].items(), key=lambda x: x[1], reverse=True),
        'checkpoint3': sorted(checkpoint_blocks_added['checkpoint3'].items(), key=lambda x: x[1], reverse=True)
    }
    sorted_main_blocks_added = sorted(main_blocks_added.items(), key=lambda x: x[1], reverse=True)

    return sorted_miner_rewards, sorted_checkpoint_blocks_added, sorted_main_blocks_added

def export_to_csv(sorted_miner_rewards, sorted_checkpoint_blocks_added, sorted_main_blocks_added):
    with open('blockchain_statistics.csv', 'w', newline='') as csvfile:
        fieldnames = ['Miner', 'Rewards', 'Checkpoint1 Blocks Added', 'Checkpoint2 Blocks Added', 'Checkpoint3 Blocks Added', 'Main Blocks Added']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        miners = set([miner for miner, _ in sorted_miner_rewards] +
                     [miner for miner, _ in sorted_checkpoint_blocks_added['checkpoint1']] +
                     [miner for miner, _ in sorted_checkpoint_blocks_added['checkpoint2']] +
                     [miner for miner, _ in sorted_checkpoint_blocks_added['checkpoint3']] +
                     [miner for miner, _ in sorted_main_blocks_added])
        
        miners = [f'miner_{i+1}' for i in range(100)]
        
        for miner in miners:
            writer.writerow({
                'Miner': miner,
                'Rewards': next((reward for m, reward in sorted_miner_rewards if m == miner), 0),
                'Checkpoint1 Blocks Added': next((count for m, count in sorted_checkpoint_blocks_added['checkpoint1'] if m == miner), 0),
                'Checkpoint2 Blocks Added': next((count for m, count in sorted_checkpoint_blocks_added['checkpoint2'] if m == miner), 0),
                'Checkpoint3 Blocks Added': next((count for m, count in sorted_checkpoint_blocks_added['checkpoint3'] if m == miner), 0),
                'Main Blocks Added': next((count for m, count in sorted_main_blocks_added if m == miner), 0)
            })

def main():
    blockchain = load_blockchain('bpowpp1.json')
    miner_rewards, checkpoint_blocks_added, main_blocks_added = calculate_statistics(blockchain)
    sorted_miner_rewards, sorted_checkpoint_blocks_added, sorted_main_blocks_added = sort_statistics(miner_rewards, checkpoint_blocks_added, main_blocks_added)
    export_to_csv(sorted_miner_rewards, sorted_checkpoint_blocks_added, sorted_main_blocks_added)
    print("Statistics exported to blockchain_statistics.csv")

if __name__ == "__main__":
    main()
