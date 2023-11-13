# pip install cryptography

import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, load_pem_private_key, load_pem_public_key
import cryptography

class CryptoLayer():
    def rsaKeypair():
        privateKey = rsa.generate_private_key(
            public_exponent = 65537, 
            key_size = 2048, 
            backend = default_backend()
            )
        return (privateKey, privateKey.public_key())

    def sign(message, privateKey):
        padded = padding.PSS(
            mgf = padding.MGF1(hashes.SHA256()), 
            salt_length = padding.PSS.MAX_LENGTH
            )
        return base64.b64encode(privateKey.sign(message, padded, hashes.SHA256()))

    def verify(message, signature, publicKey):
        signed = base64.b64decode(signature)
        padded = padding.PSS(
            mgf = padding.MGF1(hashes.SHA256()), 
            salt_length = padding.PSS.MAX_LENGTH
            )
        try:
            publicKey.verify(signed, message, padded, hashes.SHA256())
            return True
        except cryptography.exceptions.InvalidSignature:
            return False
        
    def encrypt(message, publicKey):
        cipherText = publicKey.encrypt(
            message,
            padding.OAEP(
                mgf = padding.MGF1(algorithm=hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
        return base64.b64encode(cipherText).decode("utf-8")

    def decrypt(message, privateKey):
        plaintext = privateKey.decrypt(
            base64.b64decode(message),
            padding.OAEP(
                mgf = padding.MGF1(algorithm=hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
        return plaintext.decode("utf-8")
    
    def exportKey(privateKey, publicKey):

        binaryPrivateKey = privateKey.private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm = serialization.NoEncryption()
        )
        
        binaryPublicKey = publicKey.public_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return binaryPrivateKey.decode("utf-8"), binaryPublicKey.decode("utf-8")

    def loadPublicKey(public_key_string):
        return serialization.load_pem_public_key(public_key_string, backend=default_backend())
    
    def loadPrivateKey(private_key_path):
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # Set the password if your key is encrypted
                backend=default_backend()
            )
        return private_key