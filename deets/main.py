#!/usr/bin/env python

import os
import os.path as op
import sys
import signal
import argparse

from pathlib import Path

import deets.commands   as commands
import deets.encryption as encryption
import deets.db         as deetsdb
import deets.ui         as ui


def on_sigint(*a):
    ui.printmsg('\n\nExiting (SIGINT)\n', ui.INFO)
    sys.exit(1)


__version__ = '0.2.1'


def main():

    signal.signal(signal.SIGINT, on_sigint)

    dispatch = {
        'list'     : commands.list_entries,
        'add'      : commands.add_entry,
        'get'      : commands.get_entry,
        'change'   : commands.change_entry,
        'remove'   : commands.remove_entry,
        'password' : commands.change_master_password,
        'repl'     : commands.repl_loop
    }

    args = parse_args()

    ui.printmsg(f'\ndeets password manager [{__version__}]',
                ui.EMPHASIS, ui.UNDERLINE)
    ui.printmsg('Press CTRL+C at any time to exit', ui.INFO)

    if op.exists(args.db):
        passwd = ui.prompt_password('\nEnter master password: ', ui.PROMPT)
        ui.printmsg('Loading credentials database [', ui.INFO,
                    args.db,                          ui.UNDERLINE,
                    ']\n',                            ui.INFO)

        try:
            db = deetsdb.load_database(args.db, passwd)
        except encryption.AuthenticationError:
            ui.printmsg('Authentication error - could not decrypt '
                        'credentials database!', ui.ERROR)
            sys.exit(1)
    else:
        ui.printmsg('Creating new credentials database [', ui.INFO,
                    args.db,                               ui.UNDERLINE,
                    ']\n',                                 ui.INFO)
        db = deetsdb.Database('')
        commands.change_master_password(db, args)

    dispatch[args.command](db, args)

    if db.changed:
        ui.printmsg('Saving credentials database [', ui.INFO,
                    args.db,                         ui.UNDERLINE,
                    ']\n',                           ui.INFO)
        deetsdb.save_database(db, args.db)


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    defaultdb = os.environ.get('DEETSDB', Path.home() / '.deets')

    parser = argparse.ArgumentParser('deets',
                                     description='Manage confidential details')
    parser.add_argument('-v', '--version',
                        action='version', version=__version__)
    parser.add_argument('-s', '--show', action='store_true')

    parser.add_argument('-d', '--db', metavar='FILE', default=defaultdb)

    helps = {
        'list'     : 'List all entries',
        'add'      : 'Add a new entry',
        'get'      : 'Retrieve an entry',
        'change'   : 'Modify an entry',
        'remove'   : 'Delete an entry',
        'password' : 'Change the master password',
        'repl'     : 'Run multiple commands via an interactive prompt',

        'names'    : 'Entry name(s)',
        'username' : 'Username (defaults to $DEETSUSERNAME)',
        'length'   : 'Password (defaults to $DEETSPASSWORDLENGTH)',
        'class'    : 'Password character class (defaults to $DEETSPASSWORDCLASS). ' +
                     'Can be used multiple times. Available classes: ' +
                     ','.join(encryption.PASSWORD_CHARACTER_CLASSES.keys()),
        'print'    : 'Print password to standard output instead of '
                     'copying it to the system clipboard.'
    }
    username     = os.environ.get('DEETSUSERNAME',       None)
    char_classes = os.environ.get('DEETSPASSWORDCLASS',  None)
    pwd_length   = os.environ.get('DEETSPASSWORDLENGTH', None)

    if char_classes is not None: char_classes = char_classes.split()
    if pwd_length   is not None: pwd_length   = int(pwd_length)

    configs = {
        'names'    : {'nargs'   : '*'},
        'print'    : {'action'  : 'store_true'},
        'random'   : {'action'  : 'store_true'},
        'username' : {'default' : username},
        'length'   : {'default' : pwd_length,
                      'type'    : int},
        'class'    : {'action'  : 'append',
                      'default' : char_classes,
                      'dest'    : 'char_class'}
    }

    options = {
        'list'     : [('names',), ('-p', '--print')],
        'get'      : [('names',), ('-p', '--print')],
        'add'      : [('names',),
                      ('-p', '--print'),
                      ('-u', '--username'),
                      ('-l', '--length'),
                      ('-c', '--class')],
        'change'   : [('names',),
                      ('-p', '--print'),
                      ('-l', '--length'),
                      ('-c', '--class')],
        'remove'   : [('names',)],
        'password' : [],
        'repl'     : [('-p', '--print'),
                      ('-u', '--username'),
                      ('-l', '--length'),
                      ('-c', '--class')],
    }

    subparsers = parser.add_subparsers(title='Commands', dest='command')
    for command, opts in options.items():
        subp = subparsers.add_parser(command,
                                     help=helps[command],
                                     description=helps[command])
        for flags in opts:
            name   = flags[-1].lstrip('-')
            kwargs = configs[name]
            help   = helps[  name]
            subp.add_argument(*flags, help=help, **kwargs)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.db = op.abspath(args.db)

    return args


if __name__ == '__main__':
    sys.exit(main())
