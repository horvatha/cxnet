#!/usr/bin/env python
# coding: utf-8

"""
Get pacgraph (http://kmkeen.com/pacgraph/)
You can create a file in Arch (and perhaps in Gentoo) Linux::

    pacgraph --mode=arch-repo -r

than run this script with the created filename (the same day if it possible) to
create gml file::

    python pacgraph2gml.py pacgraph.txt

"""

from __future__ import print_function
from __future__ import division
import sys
import time
import igraph
date = time.strftime("%Y-%m-%d", time.gmtime())

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit()
else:
    file = sys.argv[1]
with open(file) as f:
    string = f.readline()
dependencies = eval(string)
pkgnames = list(dependencies.keys())
for pkg in pkgnames:
    assert pkgnames.count(pkg) == 1
    for link in dependencies[pkg]["links"]:
        if link not in pkgnames:
            pkgnames.append(link)
            print("Package {0} not in keys, but it is in links.")
number_of_packages = len(pkgnames)
print("Number of packages N = {0}".format(number_of_packages))
enumdep = list(enumerate(pkgnames))
pkgname = dict(enumdep)
pkgcode = dict([(y,x) for (x,y) in enumdep])
with open("pkgnames_{0}.txt".format(date), "w") as f:
    print("\n".join(pkgnames), file=f)
edges = []
for pkg in dependencies:
    for link in dependencies[pkg]["links"]:
        linkcode = pkgcode[link]
        edges.append((pkgcode[pkg], linkcode))
M = len(edges)
print("Number of edges M =", len(edges))
print("Average degree <k> =", 2*M/number_of_packages)

net = igraph.Graph(number_of_packages, directed=True)
net.add_edges(edges)
print("Maximal degree k_max =", max(net.degree()))
net.vs["name"] = dependencies.keys()
net.write("arch_package_net_{0}.gml".format(date), format="gml") # format option is just for python3 compatibility

