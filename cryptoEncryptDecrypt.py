# pip install cryptography

import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, load_pem_private_key, load_pem_public_key
import cryptography

class CryptographicSolution():
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
        return cipherText

    def decrypt(message, privateKey):
        plaintext = privateKey.decrypt(
            message,
            padding.OAEP(
                mgf = padding.MGF1(algorithm=hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
        return plaintext
    
    def exportKey(prefix, privateKey, publicKey):

        binaryPrivateKey = privateKey.private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm = serialization.NoEncryption()
        )
        with open(prefix + '_privateKey.bin', 'wb') as f:
            f.write(binaryPrivateKey)
        
        binaryPublicKey = publicKey.public_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(prefix + '_publicKey.bin', 'wb') as f:
            f.write(binaryPublicKey)

    def importKey(keyFile, format):
        with open(keyFile, 'rb') as pemIn:
            pemRead = pemIn.read()

        if(format == 'private'):
            returnKey = load_pem_private_key(pemRead, None, default_backend())
        if(format == 'public'):
            returnKey = load_pem_public_key(pemRead)
        return returnKey


### TESTING ###

pvt1, pub1 = CryptographicSolution.rsaKeypair()
pvt2, _  = CryptographicSolution.rsaKeypair()

msg = b"Hello there!"
sig1 = CryptographicSolution.sign(msg, pvt1) # signed with private key
sig2 = CryptographicSolution.sign(msg, pvt2) # signed with *other* private key

# print(sig1)

res = CryptographicSolution.verify(msg, sig1, pub1)
print(res) #True
res = CryptographicSolution.verify(msg, sig2, pub1)
print(res) #False

testr = CryptographicSolution.encrypt(b'Hello', pub1)
print(sig1)
print(testr)

reTestr = CryptographicSolution.decrypt(testr, pvt1)
print(reTestr)

CryptographicSolution.exportKey('device1', pvt1, pub1)
publicImport = CryptographicSolution.importKey('device1_publicKey.bin', 'public')
privateImport = CryptographicSolution.importKey('device1_privateKey.bin', 'private')

print(publicImport.public_bytes(
    encoding = serialization.Encoding.PEM,
    format = serialization.PublicFormat.SubjectPublicKeyInfo))

print(privateImport.private_bytes(
    encoding = serialization.Encoding.PEM,
    format = serialization.PrivateFormat.PKCS8,
    encryption_algorithm = serialization.NoEncryption()
))

testMessage = b"Testing my imported key"
sig3 = CryptographicSolution.sign(testMessage, privateImport) # signed with private key
res = CryptographicSolution.verify(testMessage, sig3, publicImport)
print(res) #True


# , default_backend()