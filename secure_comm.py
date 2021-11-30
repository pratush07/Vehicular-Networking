from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from config import *
import os
import json


passwd = 'abc123'

private_key = None
public_key = None

def generate_keys():
    modulus_length = 6000

    if not os.path.exists(security_dir):
        os.makedirs(security_dir)

    key = RSA.generate(modulus_length)
    private_pem_path = os.path.join(security_dir, 'private_key.pem')
    with open(private_pem_path, 'wb') as f:
        f.write(key.exportKey('PEM', passwd))
    
    public_pem_path = os.path.join(security_dir, 'pub_key.pem')
    pub_key = key.publickey()
    with open(public_pem_path, 'wb') as f:
        f.write(pub_key.exportKey('PEM', passwd))

    return key, pub_key

def encrypt_public_key(a_message):
    global public_key
    if not public_key:
        public_pem_path = os.path.join(security_dir, 'pub_key.pem')
        with open(public_pem_path, 'rb') as f:
            public_key = f.read()
    
    publicKey = RSA.import_key(public_key, passwd.encode())

    encryptor = PKCS1_OAEP.new(publicKey)
    print('encrypting message ...')
    encrypted_msg = encryptor.encrypt(a_message)
    print('encrypted ...')
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    return encoded_encrypted_msg

def decrypt_private_key(encoded_encrypted_msg):
    private_pem_path = os.path.join(security_dir, 'private_key.pem')
    global private_key
    if not private_key:
        with open(private_pem_path, 'rb') as f:
            private_key = f.read()
    
    privateKey = RSA.import_key(private_key, passwd.encode())
    encryptor = PKCS1_OAEP.new(privateKey)
    print('decrypting message ...')
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decoded_decrypted_msg = encryptor.decrypt(decoded_encrypted_msg)
    print('decrypted ...')
    return decoded_decrypted_msg



# generate_keys()
# message = bytes('Hello world', 'utf-8')
# message = bytes(json.dumps({'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1}), 'utf-8')
# encoded = encrypt_public_key(message)
# print(json.loads(decrypt_private_key(encoded)))
