#!/usr/bin/env python
# coding: utf-8

"""Tests for the debnetworki.py file."""

import cxnet
import unittest
import os

class DebNetworkFunction(unittest.TestCase):
    """If we create the network during the test."""

    def setUp(self):
        self.net = cxnet.debnetwork()

    def test_types(self):
        "debnetwork should set the proper attributes"
        types = (
                ("vim", 0),
                ("nano", 0),
                ("libc6", 0),
                ("editor", 1),
                ("www-browser", 1),
                )
        self.net.cxcolorize()
        for name, _type in types:
            vertex = self.net.vs.select(name=name)[0]
            self.assertEqual(vertex["type"], _type)
            if _type == 0:
                self.assertEqual(vertex["color"], "yellow")
            else:
                self.assertEqual(vertex["color"], "lightblue")

path = os.path.split(__file__)[0]

class DebNetworkFromGML(unittest.TestCase):
    """If we read from GML."""

    def setUp(self):
        gml_file = os.path.join(path, "ubuntu-11.10-packages-2012-05-29_16.18GMT.gml")
        self.net = cxnet.Network.Read_GML(gml_file)
        self.net.normalize()

    def test_types(self):
        "debnetwork should set the proper attributes"
        types = (
                ("vim", 0),
                ("nano", 0),
                ("firefox", 0),
                ("editor", 1),
                ("www-browser", 1),
                )
        self.net.cxcolorize()
        for name, _type in types:
            vertex = self.net.vs.select(name=name)[0]
            self.assertEqual(vertex["type"], _type)
            if _type == 0:
                self.assertEqual(vertex["color"], "yellow")
                for attr in ("filesize", ):
                    self.assertTrue(isinstance(vertex["filesize"], int))
                for attr in ("priority", "section", "summary", "version"):
                    self.assertTrue(isinstance(vertex[attr], str))
            else:
                self.assertEqual(vertex["color"], "lightblue")
                for attr in ("priority", "filesize", "section", "summary", "version"):
                    self.assertEqual(vertex[attr], None)

    def test_plots(self):
        for plot in "pdf svg png".split():
            self.net.cxneighborhood("nn", plot=plot)

class Neighborhood(unittest.TestCase):
    """net.simplify(nodes, edges) function"""

    def test_return_network(self):
        net = cxnet.Network.Formula("a->b->c b->d->e")
        subnetwork = net.cxneighborhood("b", plot=False, return_network=True)
        self.assertEqual(subnetwork.vcount(), 4)

class NetworkSimplify(unittest.TestCase):
    """net.simplify(nodes, edges) function"""

    # Csomagfüggőségi hálózat füzet 14-15. oldal.
    known_values = (
            ( (),  (6,8) ),
            ( ([], []),  (6,8) ),
            ( (["virtual"],),  (5,5) ),
            ( (["virtual"], []),  (5,5) ),
            ( (["virtual", "isolated"],),  (4,5) ),
            ( (["virtual", "isolated"], []),  (4,5) ),
            ( (["isolated"], ["provides"], ),  (4,5) ),
            ( ([], ["depends"]),  (6,5) ),
            ( (["virtual"], ["recommends", "suggests"]),
                    (5,3)
              ),
            ( (["isolated"],
                 ["depends", "recommends", "provides", "suggests"]),
                 (0,0)
              ),
            ( {"edge": ["depends"]},  (6, 5) ),
            ( {"edge": ["provides", "recommends", "suggests"]},
                    (6, 3)
              ),
        )

    def basenetwork(self):
        return cxnet.Network(6,
                edges=[
                    (1,0), (0,0), (4,0),
                    (3,1),
                    (1,2), (1,2), (2,2),
                    (3,4),
                    ],
                vertex_attrs={
                    "label": list("abcdef"),
                    "name": list("abcdef"),
                    "type": [1] + [0]*5,
                    "coord" :[(0,1), (0,0), (1,0), (-1,0), (-1,1), (1,1)]
                    },
                edge_attrs={
                    "type": [ cxnet.TYPES["edge"][type_] for type_ in
                        "provides provides provides suggests depends recommends depends depends".split()
                        ]
                    },
                directed=True,
                )

    def test_known_results(self):
        "The results of simplified net should be equal the known values."
        for parameters, values in self.known_values:
            print(parameters)
            self.net = self.basenetwork()
            #cxnet.plot(self.net, vertex_color="green", layout=self.net.vs["coord"])
            if isinstance(parameters, (list, tuple)):
                self.net.cxsimplify(*parameters, test=True)
            elif isinstance(parameters, dict):
                self.net.cxsimplify(test=True, **parameters)
            else:
                raise TypeError(
                        "The type of the parameter list "
                        "is bad. Not tuple or dict.")

            vcount, ecount = values
            self.assertEqual(self.net.vcount(), vcount)
            self.assertEqual(self.net.ecount(), ecount)

class ToNetworkX(unittest.TestCase):
    """to_networkx function"""
    import networkx as nx
    known_values = {
            True: (
                ([(0,1), (1,2), (2,3), (0,2), (0,3)], [nx.DiGraph] , [nx.MultiDiGraph]),
                ([(0,0), (1,2), (2,3), (0,2), (0,3)], [nx.DiGraph] , [nx.MultiDiGraph]), # with loop
                ([(0,1), (1,2), (1,2), (0,1), (0,2)], [nx.MultiDiGraph] , []),
                ),
            False: (
                ([(0,1), (1,2), (2,3), (0,2), (0,3)], [nx.Graph] , [nx.MultiGraph]),
                ([(0,0), (1,2), (2,3), (0,2), (0,3)], [nx.Graph] , [nx.MultiGraph]), # with loop
                ([(0,1), (1,2), (2,1), (1,0), (0,2)], [nx.MultiGraph] , [nx.MultiDiGraph]),
                ([(0,1), (1,2), (1,2), (0,1), (0,2)], [nx.MultiGraph] , [nx.MultiDiGraph]),
                ),
            }

    def test_networkx_types(self):
        "The types created by to_networkx should be correct."
        for directed in [True, False]:
            #print "Directed", directed
            for edges, is_in, not_in in self.known_values[directed]:
                #print edges
                net = cxnet.Network(4, edges, directed)
                nxnet = net.to_networkx()
                for class_ in is_in:
                    self.assertIsInstance(nxnet, class_)
                for class_ in not_in:
                    self.assertNotIsInstance(nxnet, class_)

class Randomize(unittest.TestCase):
    """cxrandomize function"""
    net = cxnet.Network.Formula('a-b-c-d b-e-d')
    dirnet = cxnet.Network.Formula('a>b>c>d b>e>d')

    def test_not_keep_degrees(self):
        "cxrandomize should keep the number of nodes and edges"
        randomnet = self.net.cxrandomize()
        self.assertEqual(randomnet.vcount(), self.net.vcount())
        self.assertEqual(randomnet.ecount(), self.net.ecount())

    def test_keep_degrees(self):
        "cxrandomize should work with keep_degrees."
        net = self.net
        randomnet = net.cxrandomize(True)
        self.assertEqual(randomnet.vcount(), net.vcount())
        self.assertEqual(randomnet.ecount(), net.ecount())
        self.assertEqual(sorted(randomnet.degree()), sorted(net.degree()))

    def test_keep_degrees_directed(self):
        "cxrandomize should work with keep_degrees."
        net = self.dirnet
        randomnet = net.cxrandomize(True)
        self.assertTrue(randomnet.is_directed())
        self.assertEqual(randomnet.vcount(), net.vcount())
        self.assertEqual(randomnet.ecount(), net.ecount())
        self.assertEqual(sorted(randomnet.indegree()), sorted(net.indegree()))
        self.assertEqual(sorted(randomnet.outdegree()), sorted(net.outdegree()))

def suite():
    debnetfunction_suite = unittest.makeSuite(DebNetworkFunction)
    fromgml_suite = unittest.makeSuite(DebNetworkFromGML)
    simplify_suite = unittest.makeSuite(NetworkSimplify)
    to_networkx_suite = unittest.makeSuite(ToNetworkX)
    neighborhood_suite = unittest.makeSuite(Neighborhood)
    randomize_suite = unittest.makeSuite(Randomize)
    return unittest.TestSuite([
        debnetfunction_suite,
        fromgml_suite,
        simplify_suite,
        to_networkx_suite,
        neighborhood_suite,
        randomize_suite,
        ])

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    test()
