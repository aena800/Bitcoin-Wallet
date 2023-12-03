from datetime import datetime
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        # every new block contains the hash of the previous block
        self.previous_hash = previous_hash
        self.nonce = None
        # Calculate current hash when block is created
        self.current_hash = self.calculate_hash()  

    def calculate_hash(self):
        block_contents = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_contents.encode('utf-8')).hexdigest()
    

class Blockchain:
    def __init__(self):
        self.chain = [self.make_genesis_block()]

    def make_genesis_block(self):
        return Block(index=0, timestamp=datetime.now(), data="Genesis Block", previous_hash="0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_index = previous_block.index + 1
        new_block = Block(index=new_index, timestamp=datetime.now(), data=data, previous_hash=previous_block.calculate_hash())
        self.chain.append(new_block)
        self.save_chain_to_file()

    def get_chain(self):
        return [{'index': block.index, 'timestamp': str(block.timestamp), 'data': block.data, 'previous_hash': block.previous_hash, 'current_hash': block.current_hash} for block in self.chain]

    def save_chain_to_file(self):
        with open('blockchain_data.json', 'w') as f:
            chain_data = [{'index': block.index, 'timestamp': str(block.timestamp), 'data': block.data, 'previous_hash': block.previous_hash, 'current_hash': block.current_hash} for block in self.chain]
            json.dump(chain_data, f, indent=4)

    def load_chain_from_file(self):
        try:
            with open('blockchain_data.json', 'r') as f:
                chain_data = json.load(f)
                self.chain = []
                for block_data in chain_data:
                    block = Block(index=block_data['index'],
                                  timestamp=datetime.strptime(block_data['timestamp'], "%Y-%m-%d %H:%M:%S.%f"),
                                  data=block_data['data'],
                                  previous_hash=block_data['previous_hash'])
                    self.chain.append(block)
        except FileNotFoundError:
            self.chain = [self.make_genesis_block()]



# Create a blockchain instance
blockchain = Blockchain()
blockchain.load_chain_from_file()