from cryptography.fernet import Fernet
import json
from ..configuration.cfgRead import CREDENTIALFILE

from cryptography.fernet import Fernet
import base64
import os
import getpass
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def getKey():
    
    password_provided = getpass.getpass(prompt="Enter mail encryption password: ", stream=None)
    password = password_provided.encode()
    salt = b'K]V\xfe\x14T\xc1\x04e\xdb\xd1\xdd\xab\x95\xbe\x0c'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = Fernet(base64.urlsafe_b64encode(kdf.derive(password)))
    return key

def getCred():

    file = open(CREDENTIALFILE, 'rb')
    encrypted = file.read()
    file.close()    
    
    while True:
        key = getKey()
        try:
            decrypted=key.decrypt(encrypted)
        except BaseException as e:
            print(e)
            print("Wrong password!!")
            continue
        break

    obj = json.loads(decrypted.decode('utf-8'))
    return obj['USER'], obj['PASSWORD']
    
