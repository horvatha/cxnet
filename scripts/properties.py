#!/usr/bin/env python
# coding: utf-8

"""It prints some important properties of the files in *.gml.

This files must be in the actual directory.
"""

from __future__ import division
from __future__ import print_function
import cxnet
import glob
archive_files = glob.glob("*.gml")
print(archive_files)

def properties(archive_files, output="properties.txt"):
    lines = []
    for file_ in archive_files:
        print(file_)
        lines.append("===========\nfile = {0}\n===========\n".format(file_))
        net = cxnet.Graph.Read(file_)
        N, M = net.vcount(), net.ecount()
        deg = net.degree()
        k_max = max(deg)
        lines.append("N = {0}, M = {1}\n<k> = {2}, k_max = {3}\n".format(N, M, 2*M/N, k_max))
        C = net.transitivity_avglocal_undirected()
        C_0 = net.transitivity_local_undirected()[0]
        M_max = N * (N - 1) / 2
        p = M / M_max
        lines.append("C = {0}, C_0 = {1}\nM_max = {2} p = {3}\n".format(C, C_0, int(M_max), p))
        lines.append("\n")

        if output:
            with open(output, "a") as f:
                f.writelines(lines)

    return lines

if __name__ == "__main__":
    print("".join(properties(archive_files)))

