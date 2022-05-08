#!/usr/bin/env python


from collections import defaultdict
from pathlib import Path
import json

from . import encryption

from typing import Union, List, Tuple

pathtype = Union[str, Path]


class Database:
    def __init__(self):
        self.__entries      = {}
        self.__nameResolver = defaultdict(set)


    def __iter__(self):
        for names, credentials in self.__entries.items():
            yield names, credentials


    def all_keys(name : str) -> List[Tuple[str]]:
        return self.__nameResolver[name]


    def __setitem__(self,
                    names       : Tuple[str],
                    credentials : Tuple[str, str]):
        if names in self.__entries:
            raise KeyError(f'Entry {names} already exists')
        if sorted(set(names)) != sorted(names):
            raise KeyError(f'Duplicates in key {names}')

        self.__entries[names] = credentials

        for name in names:
            self.__nameResolver[name].add(names)


    def __getitem__(self, names : Tuple[str]) -> Tuple[str, str]:
        return self.__entries[names]


    def __delitem__(self, names : Tuple[str]):
        self.__entries.pop(names)
        for name in names:
            self.__nameResolver[name].remove(names)


def load_database(filename : pathtype,
                  password : str) -> Database:

    # load file
    # decrypt salt
    # decrypt entries
    # populate db
    with open(filename, 'rt') as f:
        text = json.load(f)

    salt    = encryption. decrypt(text['salt'].encode(), password.encode())
    entries = encryption.sdecrypt(text['entries'],       password, salt)
    entries = json.loads(entries)
    db      = Database()

    for entry in entries:
        db[tuple(entry['names'])] = (entry['username'], entry['password'])

    return db


def save_database(db       : Database,
                  filename : pathtype,
                  password : str):

    # encode entries from db
    # generate salt
    # encrypts salt
    # encrypt entries
    # save file

    entries = []

    for names, (u, p) in db:
        entries.append({
            'names'    : names,
            'username' : u,
            'password' : p})

    entries = json.dumps(entries)
    salt    = encryption.generate_salt()
    entries = encryption.sencrypt(entries, password, salt)
    salt    = encryption. encrypt(salt,    password.encode()).decode()

    with open(filename, 'wt') as f:
        f.write(json.dumps({'salt' : salt, 'entries' : entries}))
