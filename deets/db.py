#!/usr/bin/env python


from collections import defaultdict
from pathlib import Path
import itertools as it
import json

from . import encryption

from typing import Union, List, Tuple, Sequence

pathtype = Union[str, Path]


class Database:
    """Credentials database. A mapping between names/identifiers and account
    information (username+password pairs).

    Each account can be identified by multiple names. The same name may be
    used for different accounts, but the combination of names used for each
    account must be unique.

    For example, one account may have ``('amazon', 'aws')`` as its identifier,
    and another account may have ``('amazon', 'store')``.

    A ``Database`` object also stores a reference to the master password that
    was used to decrypt it, and should be used to re-encrypt it.
    """

    def __init__(self, password : str):
        self.__password     = password
        self.__entries      = {}
        self.__nameResolver = defaultdict(set)

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, password : str):
        self.__password = password


    def __iter__(self) -> Tuple[Tuple[str, ...], Tuple[str, str]]:
        for names, credentials in self.__entries.items():
            yield names, credentials


    def keys(self) -> Sequence[Tuple[str, ...]]:
        return self.__entries.keys()


    def lookup_keys(self, *names : str) -> List[Tuple[str, ...]]:
        """Returns all identifiers (each comprising one or more names) which
        contain all of the given names.
        """
        hits = it.chain(*[self.__nameResolver[n] for n in names])
        hits = [h for h in hits if all(n in h for n in names)]
        hits = sorted(set(hits))
        return hits


    def __contains__(self, names : Tuple[str, ...]) -> bool:
        names = tuple(sorted(set(names)))
        return names in self.__entries


    def __setitem__(self,
                    names       : Tuple[str, ...],
                    credentials : Tuple[str, str]):
        names = tuple(sorted(set(names)))

        if names in self.__entries:
            raise KeyError(f'Entry {names} already exists')

        self.__entries[names] = credentials

        for name in names:
            self.__nameResolver[name].add(names)


    def __getitem__(self, names : Tuple[str, ...]) -> Tuple[str, str]:
        return self.__entries[names]


    def __delitem__(self, names : Tuple[str, ...]):
        self.__entries.pop(names)
        for name in names:
            self.__nameResolver[name].remove(names)


def load_database(filename : pathtype,
                  password : str) -> Database:
    """Load and decrypt a credentials database from the specified file,
    using the given master password.

    A database is stored as a JSON file with the following structure::
        {
            "salt"    : "<salt>",
            "entries" : "<entries>"
        }

    where ``<salt>`` and ``<entries>`` are encrypted, and encded as base64
    strings.

    The ``<salt>`` is encrypted using the master password, and ``<entries>``
    encrypted using the master password, salted with (the decrypted)
    ``<salt>``.

    When decrypted, ``<entries>`` has the following structure::
        [
            {
                "names"    : ["names", "which", "identify", "this", "account"],
                "username" : "<username>",
                "password" : "<password>",
            },
            ...
        ]
    """

    with open(filename, 'rt') as f:
        text = json.load(f)

    salt    = encryption. decrypt(text['salt'].encode(), password.encode())
    entries = encryption.sdecrypt(text['entries'],       password, salt)
    entries = json.loads(entries)
    db      = Database(password)

    for entry in entries:
        db[tuple(entry['names'])] = (entry['username'], entry['password'])

    return db


def save_database(db       : Database,
                  filename : pathtype):
    """Encrypts and saves the database to file, using the
    ``Database.password``, and a randomly generated salt.
    """

    entries = []

    for names, (u, p) in db:
        entries.append({
            'names'    : names,
            'username' : u,
            'password' : p})

    entries = json.dumps(entries)
    passwd  = db.password
    salt    = encryption.generate_salt()
    entries = encryption.sencrypt(entries, passwd, salt)
    salt    = encryption. encrypt(salt,    passwd.encode()).decode()

    with open(filename, 'wt') as f:
        f.write(json.dumps({'salt' : salt, 'entries' : entries}))
