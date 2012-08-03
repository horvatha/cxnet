#!/usr/bin/env python
# coding: utf-8

"""Saves the deb software package network.

With -u or --upload argument uploades to the django server
if you have permission
"""

from __future__ import division
from __future__ import print_function
import cxnet
import sys
import os

__author__ = 'Arpad Horvath'

net = cxnet.debnetwork()
name0 = net.cxwrite(formats=["graphmlz"])
print("N = {0}, M = {1}".format(net.vcount(), net.ecount()))
if len(sys.argv) >= 2 and sys.argv[1] in ["--upload", "-u"]:
    name = os.path.join("netdata_zip", name0)
    print(name)
    os.system("Djangora-pack {name}.graphmlz".format(name=name))
    value = os.system("cp {name}.graphmlz pack".format(name=name))
    if value:
        print("I could not copy to pack subdirectory"
              " of your actual directory.")

