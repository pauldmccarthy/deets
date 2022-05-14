#!/usr/bin/env python

import sys
import readline
import getpass


# List of modifiers which can be used to change how
# a message is printed by the printmsg function.
INFO      = 1
IMPORTANT = 2
QUESTION  = 3
PROMPT    = 4
WARNING   = 5
ERROR     = 6
EMPHASIS  = 7
UNDERLINE = 8
RESET     = 9
ANSICODES = {
    INFO      : '\033[37m',         # Light grey
    IMPORTANT : '\033[92m',         # Green
    QUESTION  : '\033[36m\033[4m',  # Blue+underline
    PROMPT    : '\033[36m\033[1m',  # Bright blue+bold
    WARNING   : '\033[93m',         # Yellow
    ERROR     : '\033[91m',         # Red
    EMPHASIS  : '\033[1m',          # White+bold
    UNDERLINE : '\033[4m',          # Underline
    RESET     : '\033[0m',          # Used internally
}


def printmsg(msg='', *msgtypes, **kwargs):
    """Prints msg according to the ANSI codes provided in msgtypes.
    All other keyword arguments are passed through to the print function.

    :arg msgtypes: Message types to control formatting
    """
    msgcodes = [ANSICODES[t] for t in msgtypes]
    msgcodes = ''.join(msgcodes)
    print(f'{msgcodes}{msg}{ANSICODES[RESET]}', **kwargs)
    sys.stdout.flush()


def printmsgs(*args):

    blockids = [i for i in range(len(args)) if isinstance(args[i], str)]

    for i, idx in enumerate(blockids):
        if i == len(blockids) - 1:
            printmsg(*args[idx:])
        else:
            nextidx = blockids[i + 1]
            printmsg(*args[idx:nextidx], end='')


def prompt_password(prompt='', *msgtypes, show=False):
    printmsg(prompt, *msgtypes, end='')
    if show: return input()
    else:    return getpass.getpass(prompt='')


def prompt_input(prompt='', *msgtypes):
    printmsg(prompt, *msgtypes, end='')
    return input('')


def prompt_select(prompt, choices, labels=None):
    if labels is None:
        labels = choices
    for i, label in enumerate(labels):
        printmsgs(f'[{i + 1}]: ', EMPHASIS, label, INFO)
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

    fmtStr = ' | '.join('{{:<{}s}}'.format(l) for l in colLens)

    titles  = [col[0]  for col in columns]
    columns = [col[1:] for col in columns]

    separator = ['-' * l for l in colLens]

    printmsg(fmtStr.format(*titles), EMPHASIS)
    printmsg(fmtStr.format(*separator), EMPHASIS)

    nrows = len(columns[0])
    for i in range(nrows):

        row = [col[i] for col in columns]
        printmsg(fmtStr.format(*row), EMPHASIS)
