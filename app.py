import base58
import hashlib
from flask import Flask, request
from flask import jsonify, render_template
import wallet
from blockchain import blockchain
import transaction
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec
import json

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


# Route for Wallet Information
@app.route('/display_wallet')
def wallet_info():
    return render_template('display_wallet.html')


# Route for Creating Transactions
@app.route('/create_transaction')
def create_transaction_page():
    return render_template('create_transaction.html')


# Route for Displaying Blockchain
@app.route('/display_chain')
def display_blockchain():
    return render_template('display_chain.html')


@app.route('/generate_wallet', methods=['GET'])
def generate_wallet():
    user_wallet = wallet.Wallet()
    # Serialize the public key to PEM format
    public_key_pem = user_wallet.raw_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    private_key_pem = user_wallet.raw_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    print("pub pem: ", public_key_pem)
    print("pub pem decoded : ", public_key_pem.decode())
    return jsonify({
        'private_key': private_key_pem.decode(),
        'public_key': public_key_pem.decode()
    })


def get_transaction_history(address, blocks):
    history = []
    for block in blocks:
        # Check if the data field is a dictionary (transaction)
        if isinstance(block['data'], dict):
            tx = block['data']
            # Check if the transaction involves the given address
            if tx['sender'] == address or tx['recipient'] == address:
                history.append(tx)
    return history


def calculate_fee(transaction_amount):
    return 0.01 * transaction_amount

def calculate_balance(address, blocks):
    balance = 100  # initialized dummy balance 

    for block in blocks:
        # Check if the data is a transaction dictionary, this is to ensure we dont iterate over the genesis block
        if isinstance(block['data'], dict):
            # Extract the transaction
            tx = block['data']
            if 'recipient' in tx and 'sender' in tx and 'amount' in tx:
                 # Calculate the fee for this transaction

                fee = calculate_fee(tx['amount']) 
                # If address is the recipient, increase balance by the transaction amount (no fee)
                if tx['recipient'] == address:
                    balance += tx['amount']

                # If address is the sender, decrease balance by the transaction amount plus the fee
                if tx['sender'] == address:
                    total_amount = tx['amount'] + fee #  baance is 100, sending 10.00, +0.99 as fee => 10.99
                    balance -= total_amount     # balance = 100 -10.99

    return balance


@app.route('/fetch_wallet_info', methods=['POST'])
def fetch_wallet_info():
    user_wallet = wallet.Wallet()
    data = request.json
    print(data)
    public_address = data.get('publicKey')
    print(public_address)

    if not public_address:
        return jsonify({"error": "Missing public address"}), 400

    try:
        chain_data = blockchain.get_chain()
        print(chain_data)
        balance = calculate_balance(public_address, chain_data)
        history = get_transaction_history(public_address, chain_data)

        return jsonify({
            "publicAddress": user_wallet.address,
            "balance": balance,
            "transactionHistory": history
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/transaction_route', methods=['POST'])
def transaction_route():

    data = request.json
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = data.get('amount')
    private_key_pem = data.get('privateKey')
    # the transaction is signed using pem, whch is serialized back into raw pvt key before actually ebing used for signature
    print("Private Key (PEM):", private_key_pem)
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(), # encoding krna hai from pem to raw
        password=None,  
        backend=default_backend()
    )
    print("raw private_key: ", private_key, "\n")
    print("Recceived data:\n")
    print("sender addr: ", sender, "\n")
    print("receiver addr: ", recipient, "\n")
    print("amount: ", amount, "\n")
    
    if not all([sender, recipient, amount, private_key]):
        return jsonify({"error": "Missing data"}), 400
    fee = calculate_fee(amount)
    tx = transaction.create_transaction(sender, recipient, amount, private_key, fee)   
    # Add transaction to the blockchain
    blockchain.add_block(tx)
    return jsonify({"message": "Transaction added", "block_index": len(blockchain.chain) - 1})


# route for getting the blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = blockchain.get_chain()
    print("chain data: ", chain_data)
    return jsonify(chain_data)


@app.route('/test_key_loading')
def test_key_loading():
    try:
        pem_private_key =
        private_key = serialization.load_pem_private_key(
            pem_private_key.encode(),
            password=None,
            backend=default_backend()
        )
        print(private_key)
        return "Key loading successful"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)

