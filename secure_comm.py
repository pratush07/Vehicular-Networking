from cryptography.fernet import Fernet
from config import *
import os
import json


passwd = 'abc123'

private_key = None
public_key = None

f = Fernet(secure_key)

def encrypt_public_key(a_message):
    print('encrypting ..' + str(a_message))
    enc_message = f.encrypt(a_message)
    print(enc_message)
    return f.encrypt(enc_message)

def decrypt_private_key(encoded_encrypted_msg):
    print('decrypting ..' + str(encoded_encrypted_msg))
    msg = f.decrypt(encoded_encrypted_msg)
    print(msg)
    return msg

