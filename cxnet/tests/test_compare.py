#!/usr/bin/env python
# coding: utf-8

"""Tests for the debnetworki.py file."""

import cxnet, cxnet.debnetworki
import unittest

class DebNetworkIndegreeChanges(unittest.TestCase):
    def setUp(self):
        self.net1 = cxnet.Network.Formula("b->c->d, b->a")
        self.net2 = cxnet.Network.Formula("b->a->e, c->e")
        self.net3 = cxnet.Network.Formula("e->c, b->c->d, b->a, e->a, c->a, f->a, b->d, f->d")

    def test_indegree_list(self):
        indegree_list = cxnet.debnetworki.indegree_list(
                self.net1, self.net2)
        known_values = {"a": (1,1), "b": (0,0), "c": (1,0),
                     "d": (1, None), "e": (None, 2)}
        for vertex in known_values:
            for i in range(2):
                self.assertEqual(indegree_list[vertex][i],
                                 known_values[vertex][i])

    def test_delta_k(self):
        delta_k = cxnet.debnetworki.delta_k(self.net1, self.net2)
        #delta_k =  ((1,0), (1,-1), (0,0), )
        pairs = ((1,0), (0,0), (1,-1), )
        self.assertEqual(len(delta_k), len(pairs))
        delta_k = set(delta_k)
        for pair in pairs:
            self.assertTrue(pair in delta_k)

    def test_indegree_changes(self):
        cxnet.indegree_changes(self.net1, self.net3, outfile="temp.pdf")

if __name__ == "__main__":
        unittest.main()

