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


def suite():
    debnetfunction_suite = unittest.makeSuite(DebNetworkFunction)
    fromgml_suite = unittest.makeSuite(DebNetworkFromGML)
    simplify_suite = unittest.makeSuite(NetworkSimplify)
    return unittest.TestSuite([
        debnetfunction_suite,
        fromgml_suite,
        simplify_suite])

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    test()
