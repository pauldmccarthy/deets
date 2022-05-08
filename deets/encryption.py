#!/usr/bin/env python


import           os
import base64 as b64

from cryptography.fernet                       import Fernet
from cryptography.hazmat.primitives            import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_salt() -> bytes:
    return os.urandom(16)


def encrypt(data     : bytes,
            password : bytes,
            salt     : bytes = None) -> bytes:
    return _create_encrypter(password, salt).encrypt(data)


def decrypt(data     : bytes,
            password : bytes,
            salt     : bytes = None) -> bytes:
    return _create_encrypter(password, salt).decrypt(data)


def sencrypt(data     : str,
             password : str,
             salt     : bytes = None) -> str:

    data     = data.encode()
    password = password.encode()
    return encrypt(data, password, salt).decode()


def sdecrypt(data     : str,
             password : str,
             salt     : bytes = None) -> str:

    data     = data.encode()
    password = password.encode()
    return decrypt(data, password, salt).decode()


# https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
def _create_encrypter(password : bytes,
                      salt     : bytes = None) -> Fernet:

    if salt is None:
        salt = b'\00' * 16

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000)
    key = b64.urlsafe_b64encode(kdf.derive(password))

    return Fernet(key)
