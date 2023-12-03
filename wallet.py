import hashlib
import base58
import binascii
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class Wallet:
    # keys, balance, trans history
    def __init__(self):
        self.raw_private_key, self.raw_public_key = self.generate_key_pair()
        self.private_key_pem = self.convert_to_pem(self.raw_private_key)
        self.public_key_pem = self.raw_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.wif_private_key = self.convert_to_wif(self.private_key_pem)
        self.address = self.derive_wallet_address(self.public_key_pem)
        self.balance = 100  # Placeholder for balance
        self.transaction_history = []

    def generate_key_pair(self):
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        return private_key, public_key


    def convert_to_pem(self, private_key):   
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        return private_pem

    # a wwallet's address isnot ecxactly is pub key
    def derive_wallet_address(self, public_key_pem):
        # Step 1: Convert the PEM public key to a binary format (if it's in PEM format)
        public_key_binary = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        ).public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        # Step 2: Perform SHA-256 hashing on the binary public key
        sha256_result = hashlib.sha256(public_key_binary).digest()

        # Step 3: Perform RIPEMD-160 hashing on the result of SHA-256
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_result)
        hashed_public_key = ripemd160.digest()

        # Step 4: Perform Base58Check encoding (simplified version)
        wallet_address = base58.b58encode(hashed_public_key).decode()

        return wallet_address

    # a better way to store pvt keys
    def convert_to_wif(self, private_key_pem):
        # prefix '80' for mainnet, 'EF' for testnet
        prefixed_key = b'80' + binascii.hexlify(private_key_pem)
        # SHA-256 hash of the prefixed key
        first_sha256 = hashlib.sha256(prefixed_key).digest()
        # Second SHA-256 hash
        second_sha256 = hashlib.sha256(first_sha256).digest()
        # First 4 bytes of the second hash used as a checksum
        checksum = second_sha256[:4]
        # Append checksum to the prefixed key
        final_key = prefixed_key + checksum
        # Base58 encoding
        wif_key = base58.b58encode(final_key)
        return wif_key

    def add_transaction(self, transaction):
        # Add a transaction to the history
        self.transaction_history.append(transaction)