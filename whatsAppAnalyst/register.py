from cryptography.fernet import Fernet
import base64
import os
import json
import getpass
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from lib.configuration.cfgRead import CREDENTIALFILE

mail_user=input("Enter your mail ID: ")
mail_passwd=getpass.getpass(prompt="Enter mail password: ", stream=None)

password_provided=''
while True:
    password_provided=getpass.getpass(prompt="Enter password of encryption: ", stream=None)
    second_password_provided=getpass.getpass(prompt="Enter password again: ", stream=None)
    if password_provided!=second_password_provided:
        print("Please enter same passwords.")

    else:
        break

data='{ "USER" : ' + '"' + mail_user + '", "PASSWORD" : ' + '"' + mail_passwd + '"}'


salt = b'K]V\xfe\x14T\xc1\x04e\xdb\xd1\xdd\xab\x95\xbe\x0c'
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = Fernet(base64.urlsafe_b64encode(kdf.derive(password_provided.encode('utf-8'))))
encrypted=key.encrypt(data.encode('utf-8'))

with open(CREDENTIALFILE, 'wb+') as f:
    f.write(encrypted)