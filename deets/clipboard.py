#!/usr/bin/env python


import sys
import shlex
import subprocess as sp


def copy(text : str):
    plat = sys.platform.lower()
    if   plat == 'linux':  _copy_linux(text)
    elif plat == 'darwin': _copy_macos(text)


def _copy_macos(text : str):
    # TODO
    pass


def _copy_linux(text : str):
    sp.run(shlex.split('xsel -b -i'), text=True, input=text)
