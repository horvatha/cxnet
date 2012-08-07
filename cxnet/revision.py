#!/usr/bin/env python
# coding: utf-8

import os
import cxnet
import subprocess

def get_revision():
    for getter in [get_git_revision, get_bzr_revision]:
        revision = getter()
        if revision:
            return revision
    return ""

def cxnet_path():
    file_ = cxnet.__file__
    return os.path.join(os.path.split(file_)[0], "..")

def get_git_revision():
    os.chdir(cxnet_path())
    return command("git rev-parse HEAD").strip()

def command(x):
    return str(subprocess.Popen(x.split(' '), stdout=subprocess.PIPE).communicate()[0])

def get_bzr_revision():
    """Get the bzr revision."""

    try:
        from bzrlib.branch import Branch
        from bzrlib.errors import NotBranchError
    except ImportError:
        return None
    file_ = cxnet.__file__
    path = cxnet_path()
    try:
        b=Branch.open(path)
    except NotBranchError:
        return None
    revno, rev_id = b.last_revision_info()
    return revno

if __name__ == '__main__':
    revno, revid = get_revision()
    if revno:
        print "We are on revision {0} uploaded by {1}".format(revno, revid)
