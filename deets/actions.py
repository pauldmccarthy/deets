#!/usr/bin/env python
#


import argparse

import deets.clipboard  as clipboard
import deets.encryption as encryption
import deets.db         as deetsdb
import deets.ui         as ui


def select_account(db, args):

    names = args.names
    if names is None or len(names) == 0:
        names = ui.prompt_input('Account name(s): ', ui.PROMPT).split()
        names = deetsdb.sanitise_key(names)

    while True:
        keys = db.lookup_keys(*names)
        if len(keys) > 0:
            break

        ui.printmsg(f'No entries match [{" ".join(names)}]', ui.WARNING)
        names = ui.prompt_input('Account name(s): ', ui.PROMPT).split()

    if len(keys) == 1:
        key = keys[0]
    else:
        ui.printmsg('Multiple accounts match [', ui.WARNING,
                    ' '.join(names),             ui.IMPORTANT,
                    ']',                         ui.WARNING)
        lbls = [' '.join(k) for k in keys]
        key  = ui.prompt_select('Select an account: ', keys, lbls)

    return key


def list_entries(db : deetsdb.Database, args : argparse.Namespace):

    if args.names is None or len(args.names) == 0:
        keys = list(db.keys())
    else:
        keys = []
        for name in args.names:
            keys.extend(db.lookup_keys(name))
        keys = sorted(set(keys))

    usernames = [db[names][0]     for names in keys]
    keys      = [', '.join(names) for names in keys]

    print()
    ui.print_columns(('Account', 'Username'), (keys, usernames))
    print()


def get_entry(db : deetsdb.Database, args : argparse.Namespace):
    user, passwd = db[args.account]
    names        = ' '.join(args.account)
    clipboard.copy(passwd)
    print()
    ui.printmsgs('Account:  ', ui.EMPHASIS, names,                 ui.INFO)
    ui.printmsgs('Username: ', ui.EMPHASIS, user,                  ui.INFO)
    ui.printmsgs('Password: ', ui.EMPHASIS, 'copied to clipboard', ui.INFO)
    print()


def add_entry(db : deetsdb.Database, args : argparse.Namespace):

    names = args.names

    while names is None or len(names) == 0:
        names = ui.prompt_input('Enter account name[s]: ', ui.PROMPT).split()
        if names in db:
            print(f'Account [{" ".join(names)}] already exists!')
            names = None

    ui.printmsgs('\nAdding new account: [', ui.EMPHASIS,
                 ' '.join(names),          ui.IMPORTANT,
                 ']',                      ui.EMPHASIS)

    username  = ui.prompt_input(   'Username: ')
    password  = ui.prompt_password('Password: ', show=args.show)
    db[names] = (username, password)

    return True


def change_entry(db : deetsdb.Database, args : argparse.Namespace):
    print('change', args.name)
    return True


def remove_entry(db : deetsdb.Database, args : argparse.Namespace):
    print('remove', args.name)
    return True


def change_master_password(db : deetsdb.Database, args : argparse.Namespace):
    print('change master')
    return True
