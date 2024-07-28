import random
import json
from datetime import datetime
import uuid

class Block:
    def __init__(self, index, block_timestamp, transactions, prev_hash, miner, nonce=0, prevcheckhash=None, difficulty=4):
        self.index = index
        self.block_timestamp = block_timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.miner = miner
        self.nonce = nonce
        self.prevcheckhash = prevcheckhash
        self.difficulty = difficulty

    @property
    def hash(self):
        leading_zeros = '0' * self.difficulty
        remaining_length = 64 - self.difficulty
        return leading_zeros + ''.join(random.choices('0123456789abcdef', k=remaining_length))

class Blockchain:
    def __init__(self):
        self.zeros_difficulty = 40  # Adjusted to the correct difficulty level
        self.unconfirmed_transactions = []
        self.chain = []
        self.mining_rewards = {
            'checkpoint1': 0.05,
            'checkpoint2': 0.045,
            'checkpoint3': 0.03,
            'final': 3
        }
        self.checkpoint_limits = {
            'checkpoint1': 50,
            'checkpoint2': 25,
            'checkpoint3': 12,
            'final': 1
        }
        self.checkpoints_mined = {
            'checkpoint1': [],
            'checkpoint2': [],
            'checkpoint3': [],
            'final': []
        }
        self.checkpoint_difficulties = {
            0: self.zeros_difficulty // 8,  # checkpoint1 difficulty
            1: self.zeros_difficulty // 4,  # checkpoint2 difficulty
            2: self.zeros_difficulty // 2,  # checkpoint3 difficulty
            3: self.zeros_difficulty        # final block difficulty
        }
        self.last_main_block = None
        self.genesis_block()

    def genesis_block(self):
        genesis_block = Block(0, str(datetime.now()), [], "0", "genesis", difficulty=40)
        self.chain.append(genesis_block)
        self.last_main_block = genesis_block

    @property 
    def last_block(self):
        return self.chain[-1] if self.chain else False

    def last_checkpoint_hash(self, miner):
        for block in reversed(self.chain):
            if block.miner == miner:
                return block.hash
        return None

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

    def create_checkpoint_block(self, miner, checkpoint_level):
        checkpoint_str = f'checkpoint{checkpoint_level + 1}' if checkpoint_level < 3 else "final"
        
        # Add coinbase transaction for checkpoint reward
        reward = self.mining_rewards[checkpoint_str]
        coinbase_transaction = {
            'transaction_id': str(uuid.uuid4()),
            'transaction_timestamp': str(datetime.now()),
            'from_addr': None,
            'to_addr': miner,
            'amount': reward,
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
            prev_hash=self.last_main_block.hash if self.last_main_block else "0",
            miner=miner,
            prevcheckhash=self.last_checkpoint_hash(miner),
            difficulty=self.checkpoint_difficulties[checkpoint_level]
        )

        return new_block

    def add_block(self, block):
        if self.last_main_block or self.last_main_block.hash == block.prev_hash:
            self.chain.append(block)
            print(f"Added main block: {block.index} by {block.miner}")
            return True
        return False
    
    def add_checkpoint_block(self, block, checkpoint_num):
        checkpoint_str = f'checkpoint{checkpoint_num + 1}' if checkpoint_num < 3 else "final"
        
        self.chain.append(block)
        self.checkpoints_mined[checkpoint_str].append(block.miner)
        print(f"Added {checkpoint_str}: {block.index} by {block.miner}")
        return True

    def add_main_block(self, final_miner):
        main_block_miner = final_miner
        new_main_block = self.create_checkpoint_block(main_block_miner, 3)
        if self.add_block(new_main_block):
            self.last_main_block = new_main_block
            self.checkpoints_mined = {
                'checkpoint1': [],
                'checkpoint2': [],
                'checkpoint3': [],
                'final': []
            }

def simulate_blockchain():
    blockchain = Blockchain()
    miners = [f'miner_{i+1}' for i in range(100)]
    miner_pool_cp1 = random.sample(miners, 50)
    miner_pool_cp2 = []
    miner_pool_cp3 = []

    for block_num in range(100):
        print(f"\nSimulating block {block_num + 1}...\n")

        checkpoint1_miners = random.sample(miners, 50)
        print("Checkpoint 1")
        for miner in checkpoint1_miners:
            checkpoint1_block = blockchain.create_checkpoint_block(miner, 0)
            if checkpoint1_block:
                blockchain.add_checkpoint_block(checkpoint1_block, 0)

        checkpoint2_miners = random.sample(checkpoint1_miners, 25)
        miner_pool_cp2.extend(checkpoint2_miners)
        print("Checkpoint 2")
        for miner in checkpoint2_miners:
            checkpoint2_block = blockchain.create_checkpoint_block(miner, 1)
            if checkpoint2_block:
                blockchain.add_checkpoint_block(checkpoint2_block, 1)

        checkpoint3_miners = random.sample(checkpoint2_miners, 12)
        miner_pool_cp3.extend(checkpoint3_miners)
        print("Checkpoint 3")
        for miner in checkpoint3_miners:
            checkpoint3_block = blockchain.create_checkpoint_block(miner, 2)
            if checkpoint3_block:
                blockchain.add_checkpoint_block(checkpoint3_block, 2)

        print("Final")
        final_checkpoint_miner = random.choice(checkpoint3_miners)
        blockchain.add_main_block(final_checkpoint_miner)

    return blockchain

blockchain = simulate_blockchain()
chain_json = [block.__dict__ for block in blockchain.chain]

with open('bpowpp1.json', 'w') as json_file:
    json.dump(chain_json, json_file, indent=4)

print("Blockchain data exported to bpowpp1.json")
