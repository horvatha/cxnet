#!/usr/bin/env python
# coding: utf-8

"""Docstring of the module magyar
"""

from __future__ import division
from __future__ import print_function

from .debnetworki import Network

__author__ = 'Arpad Horvath'
# wh for def cl defs ifmain imp fr _ pdb test unittest + <Tab>

def veletlen(net):
    return Network.Erdos_Renyi(net.vcount(), m=net.ecount())

def eloszlas(net, loglog=False, **kwargs):
    dd = net.cxdegdist()
    if loglog:
        dd.set_binning('log')
        dd.bar_loglog(**kwargs)
    else:
        dd.set_binning('all')
        dd.bar_plot(**kwargs)

