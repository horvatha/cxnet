#!/usr/bin/env python
# coding: utf-8

import os
import cxnet
import subprocess

def cxnet_path():
    file_ = cxnet.__file__
    return os.path.join(os.path.split(file_)[0], "..")

def get_revision():
    for getter in [get_git_revision, get_bzr_revision]:
        revision = getter(cxnet_path())
        if revision:
            return revision
    return ""

def get_git_revision(path):
    os.chdir(path)
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
    print "Revison {0}".format(get_revision())
