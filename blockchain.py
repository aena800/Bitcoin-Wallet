from datetime import datetime
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json
import time
import threading


class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        # block number , 0 is for genesis block:
        self.index = index
        # time of bloc creation:
        self.timestamp = timestamp
        # has the transaction related data :
        self.data = data
        # every new block contains the hash of the previous block
        self.previous_hash = previous_hash
        self.nonce = nonce
        # Calculate current hash when block is created
        self.current_hash = self.calculate_hash()  

    def calculate_hash(self):
        """
        Funtion to claculate hash value for each block which depnds on various variables as used below
        """
        block_contents = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_contents.encode('utf-8')).hexdigest()
        

class Blockchain:
    # tested with diff = 3 -> block mined successfully and added
    # tested with diff = 5 -> block mined successfully and added
    # tested with diff = 7 -> block mined successfully and added

    def __init__(self, difficulty=5, max_mining_time=5*60):
        # to store the transactions in memepool before they are mined , 
        # so only if mined they can become a part of the chain
        self.mempool = []
        # the frst block in every bc is geensis block which has NO info
        # regarding trasactions but has a hash value liek others
        # however, prev hash for this oen si "0" since there is no prev block
        self.chain = [self.make_genesis_block()]

        # diffuclty can be set by assigning the number of 0's you want
        self.difficulty = difficulty

        # max_mining_time is the max time that a block will be mined for,
        # if it exceeds the limit then it would drop that block,
        # currently set to 5 mins to get the job done on cpu

        self.max_mining_time = max_mining_time

    def make_genesis_block(self):
        return Block(index=0, timestamp=datetime.now(), data="Genesis Block", previous_hash="0")

    def add_block(self, data):
        previous_block = self.chain[-1]  # the last added block
        print("last added block: ", previous_block)
        # Check if there are transactions in the pool
        if self.mempool:
            mined_block = self.mine_block(previous_block, self.mempool, self.difficulty, self.max_mining_time)
            if mined_block:  # if this value is not NONE then add the block in the chain
                self.chain.append(mined_block)
                self.mempool = []
                # saving updated blokchain
                self.save_chain_to_file()



    def mine_block(self, previous_block, data, difficulty, max_mining_time):

        """
        a form of Proof of Work. It requires computational effort to find a hash value that meets certain criteria 
        (e.g., a hash starting with a specific number of zeroes). This difficulty creates a barrier to modifying blocks

        """

        index = previous_block.index + 1
        print(index)
        timestamp = datetime.now()
        previous_hash = previous_block.current_hash 
        #previous_hash = previous_block.calculate_hash() if index > 1 else "0"
        nonce = 0
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            # is the minig time takes more than the pre-defined max time then
            # don't add that block
            if elapsed_time >= max_mining_time:
                print(f"Mining time exceeded {max_mining_time} secs for Block {index}.")
                print("Mining unsuccessful, transactions discarded.")
                self.save_chain_to_file()
                return None  # Stop mining and return None

            candidate_block = Block(index, timestamp, data, previous_hash, nonce)
            candidate_hash = candidate_block.calculate_hash()
            # '0' * difficulty = 7 for our case addds 7 zeroes
            if candidate_hash[:difficulty] == '0' * difficulty:
                print(f"Block Mined (Block {index}) with hash: {candidate_hash}")
                return candidate_block
            nonce += 1

    def get_chain(self):
        return [{'index': block.index, 'timestamp': str(block.timestamp), 
                 'data': block.data, 'previous_hash': block.previous_hash, 
                 'current_hash': block.current_hash} for block in self.chain]

    def save_chain_to_file(self):
        with open('blockchain_data.json', 'w') as f:
            chain_data = [{'index': block.index,
                           'timestamp': str(block.timestamp),
                           'data': block.data,
                           'previous_hash': block.previous_hash,
                           'nonce': block.nonce,
                           'current_hash': block.current_hash} for block in self.chain]
            json.dump(chain_data, f, indent=4)
        # Save the transaction pool
        with open('MemPool.json', 'w') as f:
            json.dump(self.mempool, f, indent=4)

    def load_chain_from_file(self):
        try:
            with open('blockchain_data.json', 'r') as f:
                chain_data = json.load(f)
                self.chain = []
                for block_data in chain_data:
                    block = Block(index=block_data['index'],
                                  timestamp=datetime.strptime(block_data['timestamp'], "%Y-%m-%d %H:%M:%S.%f"),
                                  data=block_data['data'],
                                  previous_hash=block_data['previous_hash'],
                                  nonce=block_data['nonce'])
                    self.chain.append(block)
        except FileNotFoundError:
            self.chain = [self.make_genesis_block()]

        try:
            with open('MemPool.json', 'r') as f:
                self.mempool = json.load(f)
        except FileNotFoundError:
            self.mempool = []

    def start_mining(self):
        def mining_task():
            while True:
                time.sleep(60)  # Check the mempool every 1 minute, change bhi ker sakte would make the prcess  slower
                if self.mempool:
                    previous_block = self.chain[-1]
                    print("last added block: ", previous_block)  # gives the address of the last added block in the bchain
                    new_block = self.mine_block(previous_block, self.mempool, self.difficulty, self.max_mining_time)
                    if new_block:
                        self.chain.append(new_block) # add the new block in the chain
                        self.mempool = []  # Clear the mempool after mining
                        self.save_chain_to_file()
                        print("Mined a new block and updated the blockchain.")
                    else:
                        self.mempool = []  # Clear the mempool after an attempt to mine
                    
        # Start the background thread
        mining_thread = threading.Thread(target=mining_task)
        # once started, will keep running unless u kill the terminal yourself 
        mining_thread.start()


# Create a blockchain instance
blockchain = Blockchain()
# load the stored blockchain from th json file
blockchain.load_chain_from_file()

blockchain.start_mining()
