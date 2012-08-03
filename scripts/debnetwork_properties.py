#!/usr/bin/env python
# coding: utf-8

from __future__ import division
from __future__ import print_function


"""Returns the simplified node/edge numbers in the files.
"""

__author__ = 'Arpad Horvath'
# wh for def cl defs ifmain imp fr _ pdb + <Tab>

import glob
import cxnet
import sys
import os

def run():
    outfile = "node_edge_numbers_etc2"
    if os.path.isfile(outfile):
        raise Exception("You must change the name of the output file or remove it.")
    for filename in glob.glob("./*.gml"):
        net = cxnet.load_netdata(filename)
        N, M = net.vcount(), net.ecount()
        if "updatetime" in net.attributes():
            updatetime = net["updatetime"]
        else:
            updatetime = get_updatetime(net["Description"])
        CCoeff = net.transitivity_avglocal_undirected()
        wcc = net.clusters(cxnet.WEAK)
        Nwcc = len(wcc)
        max_wcc = max(wcc.sizes())
        if "type" in net.vs.attributes():
            if not "type" in net.es.attributes():
                net.es["type"] = [0]
                N, M = 0, 0
            net.cxsimplify(vertex=["virtual"], edge=["suggests", "provides", "recommends"])
        else:
            N, M = 0, 0
        rel_size = 0 if N == 0 else max_wcc/N
        N2 = net.vcount()
        wcc2 = net.clusters(cxnet.WEAK)
        Nwcc2 = len(wcc2)
        max_wcc2 = max(wcc2.sizes())
        rel_size2 = max_wcc2/N2
        with open(outfile, "a") as f:
            print("; ".join([str(value) for value in
                [filename,
                N, M,
                N2, net.ecount(),
                CCoeff, net.transitivity_avglocal_undirected(),
                Nwcc, max_wcc, rel_size,
                Nwcc2, max_wcc2, rel_size2,
                updatetime,
                ]
                ]),
                file=f)

def get_updatetime(text):
    """Get the updatetime from the Description."""
    archiving_date = None
    nextline_update_date = nextline_archiving_date = False
    for line in text.splitlines():
        if nextline_update_date:
            return line.strip()
        if nextline_archiving_date:
            archiving_date = line.strip() + "*"
            nextline_archiving_date = False
        if line.startswith("Date"):
            nextline_date = True
            if "archiving" in line:
                nextline_archiving_date = True
            elif "update" in line:
                nextline_update_date = True
    return archiving_date


text1 = """Distribution:
 Ubuntu 10.04 lucid

Repositories (the lines beginning with deb from /etc/apt/sources.list):
 deb http://hu.archive.ubuntu.com/ubuntu/ lucid main restricted
 deb http://hu.archive.ubuntu.com/ubuntu/ lucid-updates main restricted
 deb http://hu.archive.ubuntu.com/ubuntu/ lucid universe
 deb http://hu.archive.ubuntu.com/ubuntu/ lucid-updates universe
 deb http://hu.archive.ubuntu.com/ubuntu/ lucid multiverse
 deb http://hu.archive.ubuntu.com/ubuntu/ lucid-updates multiverse
 deb http://security.ubuntu.com/ubuntu lucid-security main restricted
 deb http://security.ubuntu.com/ubuntu lucid-security universe
 deb http://security.ubuntu.com/ubuntu lucid-security multiverse

Date of archiving:
 2010-08-19 10:06:33 GMT
"""

text2 = text1 +\
"""
Date of last update (eg. apt-get update):
 2012-04-26 13:34:59 GMT
"""

def test():
    for text in [text1, text2]:
        print(get_updatetime(text))

if __name__ == '__main__':
    #test()
    run()


