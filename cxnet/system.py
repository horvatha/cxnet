#!/usr/bin/env python
# coding: utf-8

"""
(Operating) system specific staff.

The location of the setting file etc.

"""

import os

default_rc_dir = dict(
    posix=os.path.expanduser("~/.cxnet"),
    nt=os.path.expanduser("~/_cxnet"),
    )


def get_rc_dir():
    return default_rc_dir.get(os.name)


def create_rc_dir():
    rc_dir = get_rc_dir()
    if rc_dir:
        if not os.path.isdir(rc_dir):
            os.mkdir(rc_dir)
    else:
        raise NotImplementedError(
            "To create an rc directory "
            "on your platform is not implemented yet.")
    return rc_dir
