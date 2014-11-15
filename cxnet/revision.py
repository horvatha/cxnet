#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import os
import cxnet
import subprocess
from .tools import working_directory

def cxnet_path():
    file_ = cxnet.__file__
    return os.path.join(os.path.split(file_)[0], "..")

def get_revision(path=None):
    """Get the revision of the path.

    It can be git or bazaar repository.
    Parameter:
        path: string or None
            The path of the repository.  If path is None, it
            returns the revision of the cxnet package.

    """
    if path is None:
        path = cxnet_path()
    for getter in [get_git_revision, get_bzr_revision]:
        revision = getter(path)
        if revision:
            return revision
    return ""

def get_git_revision(path):
    with working_directory(path):
        return command("git rev-parse HEAD").strip()

def command(x):
    return str(subprocess.Popen(x.split(' '), stdout=subprocess.PIPE).communicate()[0])

def get_bzr_revision(path):
    """Get the bzr revision."""

    try:
        from bzrlib.branch import Branch
        from bzrlib.errors import NotBranchError
    except ImportError:
        return None
    try:
        b=Branch.open(path)
    except NotBranchError:
        return None
    revno, rev_id = b.last_revision_info()
    return revno

if __name__ == '__main__':
    print("Revison {0}".format(get_revision()))
