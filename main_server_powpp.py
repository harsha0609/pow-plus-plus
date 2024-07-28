from flask import Flask, request, jsonify
from core_blockchain_pow_pp import Block, Blockchain
from config_peers import peers
from datetime import datetime
import sys
import threading, requests
import random
import uuid, time
from ecdsa import SigningKey, SECP256k1

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False

blockchain = Blockchain()

# Dummy private and public keys for demonstration purposes
private_key = 'fc67e176ef44abc9f2539e4bdbf4fa314f0682bbc7260228fac32f78e4beecfe'
public_key = '0d29d6ef8347672c57f75438a3fefda5dfbd9e9becd6233b7d9a015d2a1827e6607707f4f7dfebf59c20f460f33543110001155140c2d9606a582d5cdda57a12'

# Generate key pairs for miners
def generate_key_pair():
    """
    Generate a new private-public key pair using SECP256k1 curve.
    """
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    return private_key, public_key

# Initialize miners with their key pairs
miners_keys = {
    'miner1': generate_key_pair(),
    'miner2': generate_key_pair(),
    'miner3': generate_key_pair()
}

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Index route that displays the port the miner is running on.
    """
    return f"Miner {port} is running"

@app.route('/chain', methods=['GET'])
def display_chain():
    """
    Return the entire blockchain as a JSON response.
    """
    blocks = [block.__dict__ for block in blockchain.chain]
    return jsonify({'blockchain': blocks, 'chain_length': len(blockchain.chain)})

@app.route('/consensus', methods=['GET'])
def chain_conflict():
    """
    Perform consensus algorithm to ensure the node's chain is the longest and valid.
    """
    if blockchain.consensus(peers):
        return "Conflict detected, Switched to longest valid chain on the network!"
    else:
        return "We are good, no conflict in blockchain!"

@app.route('/add_block', methods=['POST'])
def add_block():
    """
    Add a new block to the blockchain.
    """
    block_data = request.get_json()
    blockchain.unconfirmed_transactions = []
    block = Block(block_data['index'], block_data['block_timestamp'], block_data['transactions'], block_data['prev_hash'], block_data['miner'], block_data['nonce'], block_data['prevcheckhash'])
    added = blockchain.add_block(block)
    if not added:
        print(f"Block discarded: {block.__dict__}")
        return "The block was discarded by the node", 400
    print(f"Block added to chain: {block.__dict__}")
    return "Block added to the chain", 201

@app.route('/add_checkpoint_block', methods=['POST'])
def add_checkpoint_block():
    """
    Add a checkpoint block to the blockchain if it meets the criteria.
    """
    data = request.get_json()
    block_data = data.get('block')
    
    if not block_data:
        return jsonify({'message': 'Invalid or missing block data'}), 400
    
    block = Block(
        index=block_data['index'],
        block_timestamp=block_data['block_timestamp'],
        transactions=block_data['transactions'],
        prev_hash=block_data['prev_hash'],
        miner=block_data['miner'],
        nonce=block_data['nonce'],
        prevcheckhash=block_data['prevcheckhash']
    )
    
    added = blockchain.add_checkpoint_block(block)
    
    if added:
        print(f"Checkpoint block added from peer: {block.__dict__}")
        return jsonify({'message': 'Checkpoint block added to the chain'}), 201
    else:
        print(f"Checkpoint block from peer discarded: {block.__dict__}")
        return jsonify({'message': 'Checkpoint block discarded by the node'}), 400

@app.route('/process_transaction', methods=['POST'])
def process_transaction():
    """
    Process and add a transaction to the list of unconfirmed transactions.
    """
    readable_pk = request.form.get('pk')
    to_addr = request.form.get('to_addr')
    amount = request.form.get('amount')
    readable_sk = request.form.get('sk')
    timestamp = str(datetime.now())
    msg = {'transaction_timestamp': timestamp, 'from_addr': readable_pk, 'to_addr': to_addr, 'amount': amount}
    signature = blockchain.generate_signature(readable_sk, msg)
    signature = signature.hex()
    blockchain.unconfirmed_transactions.append({'message': msg, 'signature': signature})
    print(f"Transaction added: {msg}")
    return "Transaction has been made!"

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """
    Add a transaction to the list of unconfirmed transactions directly.
    """
    transaction_dict = request.get_json()
    blockchain.unconfirmed_transactions.append(transaction_dict)
    print(f"Transaction received and added: {transaction_dict}")
    return "Transaction added to unconfirmed_transactions and is ready to be mined!"

@app.route('/peers', methods=["GET"])
def display_peers():
    """
    Display the list of peers connected to the network.
    """
    return jsonify({'peers': str(peers), 'count': len(peers)})

@app.route('/unconfirmed_transactions', methods=["GET"])
def display_unconfirmed_transactions():
    """
    Return the list of unconfirmed transactions as a JSON response.
    """
    return jsonify({'unconfirmed_transactions': blockchain.unconfirmed_transactions})

@app.route('/start_mining', methods=['GET'])
def start_mining():
    """
    Start mining on all connected peers.
    """
    miner_identifier = request.args.get('miner', 'unknown_miner')

    def mine_on_peer(peer_url):
        """
        Send a request to start mining on a specific peer.
        """
        try:
            response = requests.get(peer_url + 'mine', params={'miner': miner_identifier})
            if response.status_code == 200:
                print(f"Mining started on node: {peer_url}")
            else:
                print(f"Failed to start mining on node: {peer_url}")
        except requests.exceptions.RequestException as e:
            print(f"Error starting mining on peer {peer_url}: {e}")

    # Create and start a thread for each peer to start mining simultaneously
    mining_threads = [threading.Thread(target=mine_on_peer, args=(peer_url,)) for peer_url in peers]
    for mining_thread in mining_threads:
        mining_thread.start()

    return "Mining has started across the network!"

@app.route('/mine', methods=['GET'])
def mine():
    """
    Handle mining for the current node and announce the mined block to peers.
    """
    mined_block = blockchain.mine(port)
    if mined_block:
        print(f"Block mined successfully: {mined_block.__dict__}")
        blockchain.announce_block(peers, mined_block)  # Announce the mined block to peers
        return jsonify({'mined_block': mined_block.__dict__}), 200
    else:
        print("Mining failed or nothing to mine")
        return "Mining failed or nothing to mine", 400

@app.route('/announce_winner', methods=['POST'])
def announce_winner():
    """
    Announce a winning block mined by a peer and add it to the blockchain.
    """
    data = request.get_json()
    winner_block = data['block']
    winner_block = Block(winner_block['index'], winner_block['block_timestamp'], winner_block['transactions'], winner_block['prev_hash'], winner_block['miner'], winner_block['nonce'])
    added = blockchain.add_block(winner_block)
    if added:
        print(f"Winner announced: {data['winner']}, Block: {winner_block.__dict__}")
        return jsonify({'message': 'Block added', 'winner': data['winner']}), 201
    print(f"Winner block discarded: {winner_block.__dict__}")
    return jsonify({'message': 'Block discarded'}), 400

@app.route('/simulate_transactions', methods=['GET'])
def simulate_transactions(python):
    """
    Simulate a batch of transactions and add them to the unconfirmed transactions list.
    """
    transactions = []
    
    for _ in range(3):
        to_addr = "random_address_" + str(random.randint(1, 1000))
        amount = str(random.uniform(1, 100))  # Random amount between 1 and 100
        fee = str(random.uniform(0.01, 1))  # Random fee between 0.01 and 1
        timestamp = str(datetime.now())
        transaction_id = str(uuid.uuid4())
        
        msg = {
            'transaction_id': transaction_id,
            'transaction_timestamp': timestamp,
            'from_addr': public_key,
            'to_addr': to_addr,
            'amount': amount,
            'fee': fee
        }
        
        signature = blockchain.generate_signature(private_key, msg).hex()
        transaction = {'message': msg, 'signature': signature}
        
        blockchain.unconfirmed_transactions.append(transaction)
        blockchain.announce_transaction(peers, transaction)
        
        transactions.append(transaction)
    
    print(f"Simulated transactions added: {transactions}")
    return jsonify({'transactions': transactions, 'status': '100 transactions simulated and added to unconfirmed transactions'})

def automate_mining_cycle(miner_port):
    """
    Automate the mining cycle: mine continuously with a pause and initiate a new cycle after a block is mined.
    """
    while True:
        # Simulate mining
        print(f"Miner {miner_port} is mining...")
        blockchain.mine(miner_port)
        # Wait before restarting the mining process
        time.sleep(5)  # Example: sleep for 5 seconds before starting a new mining cycle

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5000
    # Start mining automatically in a new thread
    threading.Thread(target=automate_mining_cycle, args=(port,)).start()
    
    app.run(port=port)
