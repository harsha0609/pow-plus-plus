import random
import json
from datetime import datetime
import uuid
import csv
from collections import defaultdict

class Block:
    def __init__(self, index, block_timestamp, transactions, prev_hash, miner, nonce=0, difficulty=40):
        self.index = index
        self.block_timestamp = block_timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.miner = miner
        self.nonce = nonce
        self.difficulty = difficulty

    @property
    def hash(self):
        leading_zeros = '0' * self.difficulty
        remaining_length = 64 - self.difficulty
        return leading_zeros + ''.join(random.choices('0123456789abcdef', k=remaining_length))

class Blockchain:
    def __init__(self):
        self.difficulty = 40  # Difficulty level for PoW
        self.chain = []
        self.unconfirmed_transactions = []
        self.mining_reward = 3.125  # Example block reward
        self.genesis_block()

    def genesis_block(self):
        genesis_block = Block(0, str(datetime.now()), [], "0", "genesis", difficulty=40)
        self.chain.append(genesis_block)

    @property 
    def last_block(self):
        return self.chain[-1] if self.chain else None

    def create_dummy_transactions(self, num_transactions):
        transactions = []
        for _ in range(num_transactions):
            transaction = {
                'transaction_id': str(uuid.uuid4()),
                'transaction_timestamp': str(datetime.now()),
                'from_addr': f'address_{random.randint(1, 1000)}',
                'to_addr': f'address_{random.randint(1, 1000)}',
                'amount': random.uniform(0.001, 1),
                'fee': random.uniform(0.0001, 0.01)
            }
            transactions.append(transaction)
        return transactions

    def create_block(self, miner):
        # Add coinbase transaction for block reward
        coinbase_transaction = {
            'transaction_id': str(uuid.uuid4()),
            'transaction_timestamp': str(datetime.now()),
            'from_addr': None,
            'to_addr': miner,
            'amount': self.mining_reward,
            'fee': 0
        }

        # Create dummy transactions
        num_dummy_transactions = random.randint(5, 10)
        dummy_transactions = self.create_dummy_transactions(num_dummy_transactions)

        transactions_to_include = [coinbase_transaction] + dummy_transactions + self.unconfirmed_transactions[:]

        new_block = Block(
            index=self.last_block.index + 1,
            block_timestamp=str(datetime.now()),
            transactions=transactions_to_include,
            prev_hash=self.last_block.hash if self.last_block else "0",
            miner=miner,
            difficulty=self.difficulty
        )

        return new_block

    def add_block(self, block):
        if self.last_block or self.last_block.hash == block.prev_hash:
            self.chain.append(block)
            return True
        return False

def simulate_blockchain():
    blockchain = Blockchain()
    miners = [f'miner_{i+1}' for i in range(100)]

    for block_num in range(100):
        miner = random.choice(miners)
        new_block = blockchain.create_block(miner)
        blockchain.add_block(new_block)

    return blockchain

def calculate_statistics(blockchain, miners):
    miner_rewards = defaultdict(float)
    blocks_added = defaultdict(int)

    for block in blockchain.chain:
        if block.index == 0:
            continue  # Skip the genesis block

        miner = block.miner
        transactions = block.transactions

        # Calculate rewards from coinbase transactions
        for txn in transactions:
            if txn['from_addr'] is None and txn['to_addr'] == miner:
                miner_rewards[miner] += txn['amount']

        # Count blocks added
        blocks_added[miner] += 1

    # Ensure all miners are included
    for miner in miners:
        if miner not in miner_rewards:
            miner_rewards[miner] = 0
        if miner not in blocks_added:
            blocks_added[miner] = 0

    return miner_rewards, blocks_added

def export_to_csv(miner_rewards, blocks_added, miners):
    with open('pow_blockchain_statistics.csv', 'w', newline='') as csvfile:
        fieldnames = ['Miner', 'Rewards', 'Blocks Added']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        for miner in miners:
            writer.writerow({
                'Miner': miner,
                'Rewards': miner_rewards.get(miner, 0),
                'Blocks Added': blocks_added.get(miner, 0)
            })

def load_blockchain(filename):
    with open(filename, 'r') as json_file:
        chain_data = json.load(json_file)
    blockchain = Blockchain()
    for block_data in chain_data:
        block = Block(**block_data)
        blockchain.chain.append(block)
    return blockchain

def main():
    blockchain = simulate_blockchain()
    chain_json = [block.__dict__ for block in blockchain.chain]

    with open('pow_blockchain.json', 'w') as json_file:
        json.dump(chain_json, json_file, indent=4)

    print("Blockchain data exported to pow_blockchain.json")

    miners = [f'miner_{i+1}' for i in range(100)]
    blockchain = load_blockchain('pow_blockchain.json')
    miner_rewards, blocks_added = calculate_statistics(blockchain, miners)
    export_to_csv(miner_rewards, blocks_added, miners)
    print("Statistics exported to pow_blockchain_statistics.csv")

if __name__ == "__main__":
    main()
