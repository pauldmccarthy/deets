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
        accounts = list(db.keys())
    else:
        accounts = []
        for name in args.names:
            accounts.extend(db.lookup_keys(name))
        accounts = sorted(set(accounts))

    usernames = [db[acct][0]           for acct in accounts]
    passwords = [db[acct][1]           for acct in accounts]
    accounts  = [f'[{" ".join(acct)}]' for acct in accounts]

    titles = ['Account', 'Username']
    cols   = [accounts, usernames]

    if args.print:
        titles.append('Password')
        cols.append(   passwords)

    print()
    ui.print_columns(titles, cols)
    print()


def get_entry(db : deetsdb.Database, args : argparse.Namespace):
    account            = select_account(db, args)
    username, password = db[account]
    account            = ' '.join(account)
    clipboard.copy(password)

    if not args.print:
        password = 'copied to clipboard'

    print()
    ui.printmsg('Account:  ', ui.INFO, account,  ui.EMPHASIS)
    ui.printmsg('Username: ', ui.INFO, username, ui.EMPHASIS)
    ui.printmsg('Password: ', ui.INFO, password, ui.EMPHASIS)
    print()


def add_entry(db : deetsdb.Database, args : argparse.Namespace):

    names = args.names

    while names is None or len(names) == 0 or names in db:
        if names in db:
            ui.printmsg('Account [',         ui.WARNING,
                        ' '.join(names),     ui.IMPORTANT,
                        '] already exists!', ui.WARNING)
        names = ui.prompt_input('Enter account name[s]: ', ui.PROMPT)
        names = names.split()
    account = deetsdb.sanitise_key(names)

    ui.printmsg('\nAdding new account: [', ui.INFO,
                ' '.join(account),         ui.IMPORTANT,
                ']',                       ui.INFO)

    username  = ui.prompt_input('Username: ', ui.PROMPT)
    if args.random:
        password = ''
    else:
        password = ui.prompt_password(
            'Password [push enter to randomly generate one]: ',
            ui.PROMPT,
            show=args.show)

    if password == '':
        ui.printmsg('Using randomly generated password', ui.INFO)
        password = encryption.generate_random_password()

    db[account] = (username, password)
    clipboard.copy(password)

    if not args.print:
        password = 'copied to clipboard'

    ui.printmsg('New account added', ui.IMPORTANT)
    ui.printmsg('Account:  ', ui.INFO, ' '.join(account), ui.EMPHASIS)
    ui.printmsg('Username: ', ui.INFO, username,          ui.EMPHASIS)
    ui.printmsg('Password: ', ui.INFO, password,          ui.EMPHASIS)
    print()


def change_entry(db : deetsdb.Database, args : argparse.Namespace):

    old_account                = select_account(db, args)
    old_username, old_password = db[old_account]

    ui.printmsg('Changing account: [', ui.WARNING,
                ' '.join(old_account), ui.IMPORTANT,
                '] (username: ',       ui.WARNING,
                old_username,          ui.IMPORTANT,
                ')',                   ui.WARNING)

    while True:
        new_account = ui.prompt_input(
            'Account name[s] [press enter to leave unchanged]: ', ui.PROMPT)
        if new_account == '':
            new_account = old_account
            break

        new_account = deetsdb.sanitise_key(new_account.split())
        if new_account in db:
            ui.printmsg('Account [',           ui.WARNING,
                        ' '.join(new_account), ui.IMPORTANT,
                        '] already exists!',   ui.WARNING)
        else:
            break

    new_username = ui.prompt_input(
        'Username [press enter to leave unchanged]: ', ui.PROMPT)
    if new_username == '':
        new_username = old_username

    if args.random:
        new_password = encryption.generate_random_password()
    else:
        new_password = ui.prompt_password(
            'Password [press enter to leave unchanged]: ', ui.PROMPT)
        if new_password == '':
            new_password = old_password

    if new_account  == old_account  and \
       new_username == old_username and \
       new_password == old_password:
        ui.printmsg('Account credentials not changed - database not modified',
                    ui.INFO)
        return

    if new_account != old_account:
        ui.printmsg('Removing account credentials [', ui.INFO,
                    old_account,                      ui.IMPORTANT,
                    ']',                              ui.INFO)
        db.delete(old_account)

    db[new_account] = (new_username, new_password)
    clipboard.copy(new_password)

    if not args.print:
        new_password = 'copied to clipboard'

    ui.printmsg('Account details changed', ui.INFO)
    ui.printmsg('Account:  ', ui.INFO, ' '.join(new_account), ui.EMPHASIS)
    ui.printmsg('Username: ', ui.INFO, new_username,          ui.EMPHASIS)
    ui.printmsg('Password: ', ui.INFO, new_password,          ui.EMPHASIS)


def remove_entry(db : deetsdb.Database, args : argparse.Namespace):
    account = select_account(db, args)

    ui.printmsg('\nRemoving account [', ui.WARNING,
                ' '.join(account),      ui.IMPORTANT,
                ']',                    ui.WARNING)

    confirm = ui.prompt_input('Are you sure? [N/y]: ', ui.PROMPT).lower()
    if confirm not in ('y', 'yes'):
        return

    db.delete(account)
    ui.printmsg('Account [',                ui.INFO,
                account,                    ui.EMPHASIS,
                '] removed from database',  ui.INFO)


def change_master_password(db : deetsdb.Database, args : argparse.Namespace):
    print('change master')
