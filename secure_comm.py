from cryptography.fernet import Fernet
from config import *
import os
import json


passwd = 'abc123'

private_key = None
public_key = None

f = Fernet(secure_key)

def encrypt_public_key(a_message):
  
    return f.encrypt(a_message)

def decrypt_private_key(encoded_encrypted_msg):

   return f.decrypt(encoded_encrypted_msg)


# generate_keys()
# message = bytes('Hello world', 'utf-8')
# message = bytes(json.dumps({'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1}), 'utf-8')
# encoded = encrypt_public_key(message)
# print(json.loads(decrypt_private_key(encoded)))
