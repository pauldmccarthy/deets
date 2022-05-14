#!/usr/bin/env python

import os
import os.path as op
import sys
import argparse
from pathlib import Path

import deets.actions as actions
import deets.db      as deetsdb
import deets.ui      as ui


__version__ = '0.0.1'

def main():

    dispatch = {
        'list'     : actions.list_entries,
        'add'      : actions.add_entry,
        'get'      : actions.get_entry,
        'change'   : actions.change_entry,
        'remove'   : actions.remove_entry,
        'password' : actions.change_master_password
    }

    args   = parse_args()
    passwd = ui.prompt_password('\nEnter master password: ', ui.PROMPT)

    if op.exists(args.db): db = deetsdb.load_database(args.db, passwd)
    else:                  db = deetsdb.Database(passwd)

    # select an existing account
    if args.command in ('get', 'change', 'remove'):
        select_account(db, args)

    if dispatch[args.command](db, args):
        ui.printmsg(f'Saving credentials database [{args.db}]', ui.INFO)
        deetsdb.save_database(db, args.db)


def select_account(db, args):
    names = args.names
    if names is None or len(names) == 0:
        while True:
            names = ui.prompt_input('Account name(s): ', ui.PROMPT).split()
            keys  = db.lookup_keys(*names)
            if len(keys) == 0:
                ui.printmsg(f'No entries match [{" ".join(names)}]',
                            ui.WARNING)
            else:
                break

    if len(keys) == 1:
        key = keys[0]
    else:
        ui.printmsg(f'Multiple accounts match [{" ".join(names)}]!',
                    ui.IMPORTANT)
        lbls = [' '.join(k) for k in keys]
        key  = ui.prompt_select('Select an account: ', keys, lbls)

    args.account = key


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser('deets',
                                     description='Manage confidential details')
    parser.add_argument('-v', '--version',
                        action='version', version=__version__)
    parser.add_argument('-s', '--show', action='store_true')

    parser.add_argument('-d', '--db', metavar='FILE',
                        default=Path.home() / '.deets')

    helps = {
        'list'     : 'List all entries',
        'add'      : 'Add a new entry',
        'get'      : 'Retrieve an entry',
        'change'   : 'Modify an entry',
        'remove'   : 'Delete an entry',
        'password' : 'Change the master password',

        'names'    : 'Entry name(s)',
        'random'   : 'Generate a random password, and copy it to the '
                     'system clipboard or print it to standard output.',
        'print'    : 'Print password to standard output instead of '
                     'copying it to the system clipboard.'
    }

    options = {
        'list'     : [(('names',),         {'nargs'  : '*'}), ],
        'get'      : [(('names',),         {'nargs'  : '*'}),
                      (('-p', '--print'),  {'action' : 'store_true'})],
        'add'      : [(('names',),         {'nargs'  : '*'}),
                      (('-r', '--random'), {'action' : 'store_true'}),
                      (('-p', '--print'),  {'action' : 'store_true'})],
        'change'   : [(('names',),         {'nargs'  : '*'}),
                      (('-r', '--random'), {'action' : 'store_true'}),
                      (('-p', '--print'),  {'action' : 'store_true'})],
        'remove'   : [(('names',),         {'nargs'  : '*'})],
        'password' : []
    }

    subparsers = parser.add_subparsers(title='Commands', dest='command')
    for command, opts in options.items():
        subp = subparsers.add_parser(command,
                                     help=helps[command],
                                     description=helps[command])
        for args, kwargs in opts:
            help = helps[args[-1].lstrip('-')]
            subp.add_argument(*args, help=help, **kwargs)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)
    return args


if __name__ == '__main__':
    sys.exit(main())
