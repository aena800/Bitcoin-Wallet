from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key


def generate_signature(private_key, data):

    signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    return signature


def create_transaction(sender, recipient, amount, private_key, fee):
    tx = {'sender': sender, 'recipient': recipient, 'amount': amount, 'fee': fee}
    signature = (generate_signature(private_key, str(tx).encode())).hex()
    tx['signature'] = signature
    return tx

