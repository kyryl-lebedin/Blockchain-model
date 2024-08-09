import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = [] # intermediate storage for transactions
        self.create_block(proof=1, previous_hash='0') 
        self.nodes = set() # set to store the nodes in the blockchain network


    # functionality for creating a block, not mining
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions # takes all the transactions from the intermediate storage
        }
        self.transactions = [] 
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    #mechanical class functionality
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender, 'receiver': receiver, 'amount': amount}) # better turn transaction into object
        return self.get_previous_block()['index'] + 1 # returns the index of the block that will hold this transaction
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) 

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain') # get chain of specific node defined by ip
            if response.status_code == 200:
                length = response.json()['length'] # length of chain of specific node
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain # choose the chain that mined the most blocks
        if longest_chain: # means it's not none and replacement was made
            self.chain = longest_chain
            return True
        return False # if there is no bigger chains

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

node_adress = str(uuid4()).replace('-', '') # address to recieve coins for creating blocks, fees from transactions in it

# every node has a server. chain is initialized for every node.
blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    # in out bc system automatically allocates 1 coin to the miner
    blockchain.add_transaction(sender=node_adress, receiver='Miner', amount=1) 

    # after block is mined, we create a new block
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],

        'transactions': block['transactions'] 
    }
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {
            'message': 'The blockchain is valid.'
        }
    else:
        response = {
            'message': 'The blockchain is not valid.'
        }
    return jsonify(response), 200

# actual tool for adding transactions
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount']) # cause it returns the index of the block it will be added in

    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201

# post file with adresses {nodes: ['http://, ...]}
# synchronize with all the nodes in blockchain (all the nodes that stated in json)
# this allows to imitate other nodes on network
# adds all the others nodes on the network to local server
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json() # json file with all the nodes
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# function to synchronize the chain on this node
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain() # not only returns bool but also replaces node's chain if needed
    if is_chain_replaced: 
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000)


