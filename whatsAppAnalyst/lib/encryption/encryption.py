from cryptography.fernet import Fernet
import base64
import os
import getpass
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Key():

    _instance=None
    key=None    

    def __new__(self):

        if not self._instance:
            self._instance=super(Key, self).__new__(self)
            Key.checkBytes=b'gAAAAABelHf6y5_LgvxK7TDoa9xoFFexiWvK9oqcMwSAnmABib9IGB3iRn14UJtMUhUC0UX5JS2FOCxBd-iKit9Ul779xtIddQ=='
            Key.key=Key.genKey()
            
        return self._instance

    def getKey(self):
        return self.key

    @staticmethod
    def genKey():

        while True:
            password_provided=getpass.getpass(prompt="Enter password for this session: ", stream=None)
            second_password_provided=getpass.getpass(prompt="Enter password again: ", stream=None)
            if password_provided!=second_password_provided:
                print("Please enter same passwords.")

            else:
                print("Session started successfully!!")
                break

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

def encryptBytes(data):
    
    return newkey.key.encrypt(data)


def decryptBytes(encrypted):

    return newkey.key.decrypt(encrypted)

newkey=Key()