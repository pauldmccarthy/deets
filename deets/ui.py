#!/usr/bin/env python

import sys
import readline
import getpass


# List of modifiers which can be used to change how
# a message is printed by the printmsg function.
INFO      = object()
IMPORTANT = object()
QUESTION  = object()
PROMPT    = object()
WARNING   = object()
ERROR     = object()
EMPHASIS  = object()
UNDERLINE = object()
RESET     = object()
ANSICODES = {
    INFO      : '\033[37m',         # Light grey
    IMPORTANT : '\033[92m\033[1m',  # Green+bold
    QUESTION  : '\033[36m\033[4m',  # Blue+underline
    PROMPT    : '\033[36m\033[1m',  # Bright blue+bold
    WARNING   : '\033[93m\033[1m',  # Yellow+bold
    ERROR     : '\033[91m',         # Red
    EMPHASIS  : '\033[1m',          # White+bold
    UNDERLINE : '\033[4m',          # Underline
    RESET     : '\033[0m',          # Used internally
}


def printmsg(*args, **kwargs):
    """Prints a sequence of strings according to the ANSI codes provided in
    msgtypes. Expects positional arguments to be of the form::

        printable, ANSICODE, printable, ANSICODE, ...

    :arg msgtypes: Message types to control formatting
    """

    args     = list(args)
    blockids = [i for i in range(len(args)) if (args[i] not in ANSICODES)]

    for i, idx in enumerate(blockids):
        if i == len(blockids) - 1:
            slc = slice(idx + 1, None)
        else:
            slc = slice(idx + 1, blockids[i + 1])

        msg      = args[idx]
        msgcodes = args[slc]
        msgcodes = [ANSICODES[c] for c in msgcodes]
        msgcodes = ''.join(msgcodes)

        print(f'{msgcodes}{msg}{ANSICODES[RESET]}', end='')

    print(**kwargs)
    sys.stdout.flush()


def prompt_password(prompt='', *msgtypes, show=False):
    printmsg(prompt, *msgtypes, end='')
    if show: response = input().strip()
    else:    response = getpass.getpass(prompt='').strip()
    if response == '':
        print()
    return response


def prompt_input(prompt='', *msgtypes, default=None):
    printmsg(prompt, *msgtypes, end='')
    response = input('').strip()

    if response == '':
        print()

    if (default is not None) and (response == ''): return default
    else:                                          return response


def prompt_select(prompt, choices, labels=None):
    if labels is None:
        labels = choices
    for i, label in enumerate(labels):
        printmsg(f'[{i + 1}]: ', EMPHASIS, label, INFO)
    while True:
        select = prompt_input(prompt, PROMPT)
        try:    select = int(select) - 1
        except: continue
        if select < 0 or select >= len(choices):
            continue
        break
    return choices[select]


def print_columns(titles, columns):
    """Convenience function which pretty-prints a collection of columns in a
    tabular format.

    :arg titles:  A list of titles, one for each column.

    :arg columns: A list of columns, where each column is a list of strings.
    """

    cols  = []

    for t, c in zip(titles, columns):
        cols.append([t] + list(map(str, c)))

    columns = cols
    colLens = []

    for col in columns:
        maxLen = max([len(r) for r in col])
        colLens.append(maxLen)

    fmtStrs = ['{{:<{}s}}'.format(l) for l   in colLens]
    titles  = [col[0]                for col in columns]
    rowsep  = ['-' * l               for l   in colLens]
    columns = [col[1:]               for col in columns]

    def printrow(vals, *msgtypes):
        for i, (val, fmtStr) in enumerate(zip(vals, fmtStrs)):
            printmsg(fmtStr.format(val), *msgtypes, end='')
            if i < len(vals) - 1:
                printmsg(' | ', INFO, end='')
        print()

    printrow(titles, EMPHASIS)
    printrow(rowsep, INFO)

    nrows = len(columns[0])
    for i in range(nrows):
        row = [col[i] for col in columns]
        printrow(row, IMPORTANT)
