#!/usr/bin/env python
# coding: utf-8
from __future__ import division

__author__ = """Arpad Horvath <horvath.arpad@roik.bmf.hu>\n"""
#    Copyright (C) 2009 by Arpad Horvath <horvath.arpad@roik.bmf.hu>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import sys
sys.path.insert(0, "..")
#import networkx

class ClusteringCoefficient:
    """Clustering coefficient of an undirected network.
    """

    def __init__(self, network, verbose=True):
        """Make the clustering coefficient.

        Input:
          network: the investigated network (MyDiGraph)
        """

        self.network = network
        self.verbose = verbose

    def clustering_coefficient(self, node=None):
        """Returns with clustering coefficient list of the graph or cc properties of node.

        Parameters:
          if node is given, returns with the cc properties of the node
          if node is not given, it returns with the list of cc.

        Output:
          for node: a tuple of (number_of_neighbours, edges, clustering_coefficient)
          for the whole graph: list of clustering coefficients.
        """

        if node is not None:
            neigh = self.network.neighbors(node)
            subgraph = self.network.subgraph(neigh)
            n = len(neigh)

            edges = subgraph.number_of_edges()

            max_edges = n*(n-1)
            coefficient = 0 if n in [0,1] else edges / max_edges
            return (n, edges, coefficient)

        else:
            cc_list = []
            for node in self.network:
                neighbors, edges, clustering_coeff = self.clustering_coefficient(node)
                cc_list.append(clustering_coeff)
            return cc_list

    def avg_clustering_coefficient(self):
        """Returns with the average clustering coefficient.

        This is defined in:
        Réka Albert and Albert-László Barabasi:
        Statistical mechanics of complex networks,
        REVIEWS OF MODERN PHYSICS, VOLUME 74, JANUARY 2002
        Page 49
        """
        c = self.clustering_coefficient()
        return sum(c) / len(c)


if __name__ == "__main__":
    import packages
    g=packages.get_graph()
    cc = ClusteringCoefficient(g)
    print("Clustering coeff. for vim is {0}".format(cc.clustering_coefficient("vim")[2]))
    acc = cc.avg_clustering_coefficient()
    print(acc)

    N, M = g.number_of_nodes(), g.number_of_edges()
    print "%d él és %d él van a hálózatban."
