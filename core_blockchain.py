from hashlib import sha256
from datetime import datetime
from ecdsa import SigningKey, SECP256k1, VerifyingKey
import json, uuid
import requests
from flask import request

# Dummy private and public keys for demonstration purpose
private_key = 'fc67e176ef44abc9f2539e4bdbf4fa314f0682bbc7260228fac32f78e4beecfe'
public_key = '0d29d6ef8347672c57f75438a3fefda5dfbd9e9becd6233b7d9a015d2a1827e6607707f4f7dfebf59c20f460f33543110001155140c2d9606a582d5cdda57a12'


class Block:
    def __init__(self, index, block_timestamp, transactions, prev_hash, miner, nonce=0):
        """
        Initialize a block with its attributes.

        Args:
            index (int): Index of the block in the blockchain.
            block_timestamp (str): Timestamp of when the block was created.
            transactions (list): List of transactions included in the block.
            prev_hash (str): Hash of the previous block in the blockchain.
            miner (str): The identifier of the miner who mined the block.
            nonce (int): Nonce used in mining.
        """
        self.index = index
        self.block_timestamp = block_timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.miner = miner
        self.nonce = nonce

    @property 
    def hash(self):
        """
        Calculate the hash of the block using SHA-256.

        Returns:
            str: Hash of the block.
        """
        block_string = str(self.index) + str(self.block_timestamp) + str(self.transactions) + str(self.prev_hash) + str(self.miner) + str(self.nonce)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        """
        Initialize the blockchain with its attributes.
        """
        self.zeros_difficulty = 6  # Number of leading zeros required for proof of work
        self.unconfirmed_transactions = []  # List to store unconfirmed transactions
        self.chain = []  # List to store blocks in the blockchain
        self.mining_reward = 3.125  # Define a fixed mining reward
        self.genesis_block()  # Create the genesis block

    def genesis_block(self):
        """
        Create the genesis block, which is the first block in the blockchain.
        """
        g_block = Block(0, str(0), [], 0, 'genesis_miner', 0)
        self.chain.append(g_block)

    @property 
    def last_block(self):
        """
        Get the last block in the blockchain.

        Returns:
            Block: The last block in the blockchain.
        """
        if self.chain:
            return self.chain[-1]
        else:
            return False
    
    def add_block(self, block):
        """
        Add a block to the blockchain if it is valid.

        Args:
            block (Block): Block to be added to the blockchain.

        Returns:
            bool: True if the block was added successfully, False otherwise.
        """
        if self.last_block and self.last_block.hash == block.prev_hash:
            if self.is_valid_proof(block):
                self.chain.append(block)
                return True
        return False

    def mine(self, miner):
        """
        Mine a new block by adding all unconfirmed transactions and finding a valid proof of work.

        Args:
            miner (str): The identifier of the miner.

        Returns:
            Block or False: The mined block if successful, False if there are no unconfirmed transactions.
        """
        if not self.unconfirmed_transactions:
            return False
        
        
        
        for transaction in self.unconfirmed_transactions:
            if not self.is_valid_transaction(transaction): 
                self.unconfirmed_transactions.remove(transaction)
        
        # Add a coinbase transaction to reward the miner
        coinbase_transaction = {
            'transaction_id': str(uuid.uuid4()),
            'transaction_timestamp': str(datetime.now()),
            'from_addr': None,
            'to_addr': miner,
            'amount': self.mining_reward,
            'fee': 0
        }
        coinbase_transaction_signature = self.generate_signature(private_key, coinbase_transaction).hex()
        coinbase_transaction['signature'] = coinbase_transaction_signature
        
        # Include the coinbase transaction at the beginning of the list of transactions
        transactions_to_include = [coinbase_transaction] + self.unconfirmed_transactions[:]

        new_block = Block(index=self.last_block.index + 1, block_timestamp=str(datetime.now()),
                          transactions=transactions_to_include, prev_hash=self.last_block.hash, miner=miner)

        hash_val = new_block.hash
        print("started mining", hash_val)
        while not hash_val.startswith('0' * self.zeros_difficulty):
            new_block.nonce += 1
            hash_val = new_block.hash
        
        print("finished mining", new_block.nonce, hash_val)
        self.unconfirmed_transactions = []
        return new_block
    
        # else:
        #     for transaction in self.unconfirmed_transactions:
        #         if not self.is_valid_transaction(transaction): 
        #             self.unconfirmed_transactions.remove(transaction)

        #     new_block = Block(index=self.last_block.index + 1, block_timestamp=str(datetime.now()),
        #                       transactions=self.unconfirmed_transactions, prev_hash=self.last_block.hash, miner=miner)

        #     hash_val = new_block.hash
        #     print("started mining", hash_val)
        #     while not hash_val.startswith('0' * self.zeros_difficulty):
        #         new_block.nonce += 1
        #         hash_val = new_block.hash
            
        #     print("finished mining", new_block.nonce, hash_val)
        #     self.unconfirmed_transactions = []
        #     return new_block
    
    def is_valid_proof(self, block):
        """
        Check if the hash of a block meets the proof of work requirement.

        Args:
            block (Block): Block to be validated.

        Returns:
            bool: True if the block hash meets the proof of work requirement, False otherwise.
        """
        return block.hash.startswith('0' * self.zeros_difficulty)

    def is_valid_chain(self):
        """
        Validate the entire blockchain except for the genesis block.

        Returns:
            bool: True if the blockchain is valid, False otherwise.
        """
        for i in range(1, len(self.chain)):
            if not self.is_valid_proof(self.chain[i]):
                return False
            if self.chain[i].prev_hash != self.chain[i - 1].hash:
                return False
        return True

    def is_valid_transaction(self, transaction_dict):
        """
        Verify the validity of a transaction by checking its signature.

        Args:
            transaction_dict (dict): Dictionary representing the transaction.

        Returns:
            bool: True if the transaction is valid, False otherwise.
        """
        signature = transaction_dict['signature']
        signature = bytes.fromhex(signature)  # Convert hex string back to bytes
        public_key = transaction_dict['message']['from_addr']
        public_key = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1)  # Get public key in bytes
        msg = json.dumps(transaction_dict['message']).encode()  # Convert message back to bytes
        if public_key.verify(signature, msg):
            return True
        return False

    def create_temp_chain(self, blockchain_list):
        """
        Create a temporary Blockchain object based on a list of blocks received.

        Args:
            blockchain_list (list): List of block dictionaries representing the blockchain.

        Returns:
            Blockchain: Temporary Blockchain object created from the list of blocks.
        """
        temp_blockchain = Blockchain()
        for block in blockchain_list[1:]:
            temp_block = Block(block['index'], block['block_timestamp'], block['transactions'], block['prev_hash'], block['miner'], block['nonce'])
            temp_blockchain.add_block(temp_block)
        return temp_blockchain

    def consensus(self, peers):
        """
        Find the longest valid chain among all peers and switch to it if necessary.

        Args:
            peers (list): List of peer URLs.

        Returns:
            bool: True if the chain was updated, False otherwise.
        """
        longest_chain = self.chain
        for peer in peers:
            if peer != request.host_url:
                response = requests.get(peer + 'chain')
                chain = response.json()['blockchain']
                temp_blockchain = self.create_temp_chain(chain)
                if len(temp_blockchain.chain) > len(longest_chain) and temp_blockchain.is_valid_chain(): 
                    longest_chain = temp_blockchain.chain
        
        if longest_chain != self.chain:
            self.chain = longest_chain
            return True
        return False

    def announce_block(self, peers, block_obj):
        """
        Announce a mined block to other peers in the network.

        Args:
            peers (list): List of peer URLs.
            block_obj (Block): Mined block to be announced.
        """
        for peer in peers:
            try:
                response = requests.post(peer + 'add_block', json=block_obj.__dict__)
                if response.status_code == 201:
                    print(f"Block successfully announced to {peer}")
                else:
                    print(f"Failed to announce block to {peer}")
            except requests.exceptions.RequestException as e:
                print(f"Error announcing block to peer {peer}: {e}")

    def generate_signature(self, readable_sk, msg):
        """
        Generate a signature for a message using a private key.

        Args:
            readable_sk (str): Readable format of the private key.
            msg (dict): Message to be signed.

        Returns:
            str: Hexadecimal representation of the signature.
        """
        sk = SigningKey.from_string(bytes.fromhex(readable_sk), curve=SECP256k1)
        msg = json.dumps(msg).encode()
        return sk.sign(msg)

    def announce_transaction(self, peers, transaction_dict):
        """
        Announce a transaction to other peers in the network.

        Args:
            peers (list): List of peer URLs.
            transaction_dict (dict): Transaction dictionary to be announced.
        """
        for peer in peers:
            response = requests.post(peer + 'add_transaction', json=transaction_dict)

