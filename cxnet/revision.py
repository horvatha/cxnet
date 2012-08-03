#!/usr/bin/env python
# coding: utf-8

import os
import cxnet

def get_revision():
    """Get the bzr revision."""

    try:
        from bzrlib.branch import Branch
        from bzrlib.errors import NotBranchError
    except ImportError:
        return (None, None)
    file_ = cxnet.__file__
    path = os.path.join(os.path.split(file_)[0], "..")
    try:
        b=Branch.open(path)
    except NotBranchError:
        return (None, None)
    revno, rev_id = b.last_revision_info()
    return (revno, rev_id)

if __name__ == '__main__':
    revno, revid = get_revision()
    if revno:
        print "We are on revision {0} uploaded by {1}".format(revno, revid)
