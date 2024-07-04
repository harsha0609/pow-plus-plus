from flask import Flask, request, jsonify, url_for, render_template
from core_blockchain import Block, Blockchain
from config_peers import peers
from datetime import datetime
import sys
import threading, requests

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False

blockchain = Blockchain()

# Dummy private and public keys for demonstration purposes
private_key = 'fc67e176ef44abc9f2539e4bdbf4fa314f0682bbc7260228fac32f78e4beecfe'
public_key = '0d29d6ef8347672c57f75438a3fefda5dfbd9e9becd6233b7d9a015d2a1827e6607707f4f7dfebf59c20f460f33543110001155140c2d9606a582d5cdda57a12'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return url_for('process_transaction')
    else:
        return render_template('make_transaction.html')

@app.route('/chain', methods=['GET'])
def display_chain():
    blocks = [block.__dict__ for block in blockchain.chain]
    return jsonify({'blockchain': blocks, 'chain_length': len(blockchain.chain)})

@app.route('/consensus', methods=['GET'])
def chain_conflict():
    if blockchain.consensus(peers):
        return "Conflict detected, Switched to longest valid chain on the network!"
    else:
        return "We are good, no conflict in blockchain!"

@app.route('/add_block', methods=['POST'])
def add_block():
    block_data = request.get_json()
    blockchain.unconfirmed_transactions = []
    block = Block(block_data['index'], block_data['block_timestamp'], block_data['transactions'], block_data['prev_hash'], block_data['miner'], block_data['nonce'])
    added = blockchain.add_block(block)
    if not added:
        print(f"Block discarded: {block.__dict__}")
        return "The block was discarded by the node", 400
    print(f"Block added to chain: {block.__dict__}")
    return "Block added to the chain", 201

@app.route('/process_transaction', methods=['POST'])
def process_transaction():
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
    transaction_dict = request.get_json()
    blockchain.unconfirmed_transactions.append(transaction_dict)
    print(f"Transaction received and added: {transaction_dict}")
    return "Transaction added to unconfirmed_transactions and is ready to be mined!"

@app.route('/peers', methods=["GET"])
def display_peers():
    return jsonify({'peers': str(peers), 'count': len(peers)})

@app.route('/unconfirmed_transactions', methods=["GET"])
def display_unconfirmed_transactions():
    return jsonify({'unconfirmed_transactions': blockchain.unconfirmed_transactions})

@app.route('/start_mining', methods=['GET'])
def start_mining():
    miner_identifier = request.args.get('miner', 'unknown_miner')

    def mine_on_peer(peer_url):
        try:
            response = requests.get(peer_url + 'mine', params={'miner': miner_identifier})
            if response.status_code == 200:
                print(f"Mining started on node: {peer_url}")
            else:
                print(f"Failed to start mining on node: {peer_url}")
        except requests.exceptions.RequestException as e:
            print(f"Error starting mining on peer {peer_url}: {e}")

    # Create a thread for each peer to start mining simultaneously
    mining_threads = [threading.Thread(target=mine_on_peer, args=(peer_url,)) for peer_url in peers]
    
    # Start all mining threads
    for mining_thread in mining_threads:
        mining_thread.start()

    return "Mining has started across the network!"

@app.route('/mine', methods=['GET'])
def mine():
    # miner_identifier = request.args.get('miner', 'unknown_miner')
    mined_block = blockchain.mine(port)
    if mined_block:
        print(f"Block mined successfully: {mined_block.__dict__}")
        blockchain.announce_block(peers, mined_block)  # Announce the mined block to peers
        # winner = {'winner': request.host_url, 'block': mined_block.__dict__}
        # for peer in peers:
        #     try:
        #         response = requests.post(peer + 'announce_winner', json=winner)  # Announce the winner to other peers
        #         if response.status_code == 201:
        #             print(f"Block successfully announced to {peer}")
        #         else:
        #             print(f"Failed to announce block to {peer}")
        #     except requests.exceptions.RequestException as e:
        #         print(f"Error announcing block to peer {peer}: {e}")
        return jsonify({'mined_block': mined_block.__dict__}), 200
    else:
        print("Mining failed or nothing to mine")
        return "Mining failed or nothing to mine", 400

@app.route('/announce_winner', methods=['POST'])
def announce_winner():
    data = request.get_json()
    winner_block = data['block']
    winner_block = Block(winner_block['index'], winner_block['block_timestamp'], winner_block['transactions'], winner_block['prev_hash'], winner_block['miner'], winner_block['nonce'])
    added = blockchain.add_block(winner_block)
    if added:
        print(f"Winner announced: {data['winner']}, Block: {winner_block.__dict__}")
        return jsonify({'message': 'Block added', 'winner': data['winner']}), 201
    print(f"Winner block discarded: {winner_block.__dict__}")
    return jsonify({'message': 'Block discarded'}), 400
import random
import uuid

@app.route('/simulate_transactions', methods=['GET'])
def simulate_transactions():
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5000
    print(f"Starting node on port {port}")
    app.run(host="127.0.0.1", port=port)
