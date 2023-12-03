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
transaction_info = {}


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


def get_transaction_history(address, blockchain):
    actual_history = []
    secret_history = []
    tx_index = 0
    for block in blockchain.chain:
        if block.data == "Genesis Block":
            continue
        for tx_hash in block.data:
            tx = transaction_info.get(tx_hash, {})
            if tx.get('sender') == address or tx.get('recipient') == address:
                
                actual_history.append({"T# ": tx_index, "Data": tx})
                secret_history.append({"T# ": tx_index, "Data": tx_hash})
                tx_index += 1
    return actual_history, secret_history


def calculate_fee(transaction_amount):
    return 0.01 * transaction_amount


def calculate_balance(address, blockchain):
    balance = 100  # Initial balance
    for block in blockchain.chain:
        if block.data == "Genesis Block":
            continue
        for tx_hash in block.data:
            tx = transaction_info.get(tx_hash, {})
            if tx.get('recipient') == address:
                balance += tx.get('amount', 0)
            if tx.get('sender') == address:
                balance -= (tx.get('amount', 0) + tx.get('fee', 0))
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
        balance = calculate_balance(public_address, blockchain)
        actual_history, secret_history = get_transaction_history(public_address, blockchain)

        return jsonify({
            "publicAddress": user_wallet.address,
            "balance": balance,
            "transactionHistory": secret_history
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
    private_key_pem = '\n-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEILTIaRpea+Ept1Ji8A2uXlUj8+umr/v6Lqup4FHP/8W+oAoGCCqGSM49AwEHoUQDQgAEkydMHBHq2UNfGDM/gcRkYkF9JD+hxsuU4ra0+NZgg0VJ9hxZqOyXjzBHCVumfsgL28Bu9UOihB2HzotfPpdxSg==\n-----END EC PRIVATE KEY-----\n'
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
    # Add the transaction hash to the mempool
    transaction_json = json.dumps(tx, sort_keys=True).encode()
    transaction_hash = hashlib.sha256(transaction_json).hexdigest()
    blockchain.mempool.append(transaction_hash)

    # Store the full transaction in transaction_info
    transaction_info[transaction_hash] = tx

    return jsonify({"message": "Transaction added to the pool", "pool_size": len(blockchain.mempool)})


# route for getting the blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = blockchain.get_chain()
    print("chain data: ", chain_data)
    return jsonify(chain_data)


@app.route('/test_key_loading')
def test_key_loading():
    try:
        pem_private_key = """"""
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

