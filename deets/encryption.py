#!/usr/bin/env python


import           os
import base64 as b64
import           string
import           secrets

from typing import Sequence

from cryptography.fernet                       import Fernet, InvalidToken
from cryptography.hazmat.primitives            import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_salt() -> bytes:
    return os.urandom(16)


PASSWORD_CHARACTER_CLASSES = {
    'uppercase'   : string.ascii_uppercase,
    'lowercase'   : string.ascii_lowercase,
    'numbers'     : string.digits,
    'punctuation' : string.punctuation,
}
PASSWORD_CLASS_TESTS  = {
    'uppercase'   : str.isupper,
    'lowercase'   : str.islower,
    'numbers'     : str.isdigit,
    'punctuation' : lambda c: c in string.punctuation
}


# TODO conform to different constraints selected by user
#      (e.g. min/max length, allowable characters, etc)
def generate_random_password(length  : int           = None,
                             classes : Sequence[str] = None) -> str:

    if length  is None: length  = 20
    if classes is None: classes = ['uppercase', 'lowercase', 'numbers']

    if len(classes) < 1 or \
       any(c not in PASSWORD_CHARACTER_CLASSES for c in classes):
        raise ValueError(f'{classes}')

    chars = ''
    tests = []
    for cls in classes:
        chars += PASSWORD_CHARACTER_CLASSES[cls]
        tests.append(PASSWORD_CLASS_TESTS[  cls])

    chars = ''.join(chars)

    # Taken from the python secrets module documentation
    while True:
        password = ''.join(secrets.choice(chars) for i in range(length))
        if any(c.islower() for c in password) and \
           any(c.isupper() for c in password) and \
           sum(c.isdigit() for c in password) >= 3:
            break
    return password


class AuthenticationError(Exception):
    pass


def encrypt(data     : bytes,
            password : bytes,
            salt     : bytes = None) -> bytes:
    """Encrypt a byte sequence. """
    return _create_encrypter(password, salt).encrypt(data)


def decrypt(data     : bytes,
            password : bytes,
            salt     : bytes = None) -> bytes:
    """Decrypt a byte sequence. """
    try:
        return _create_encrypter(password, salt).decrypt(data)
    except InvalidToken:
        raise AuthenticationError()


def sencrypt(data     : str,
             password : str,
             salt     : bytes = None) -> str:
    """Encrypt a string. """
    data     = data.encode()
    password = password.encode()
    return encrypt(data, password, salt).decode()


def sdecrypt(data     : str,
             password : str,
             salt     : bytes = None) -> str:
    """Decrypt a string. """
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
