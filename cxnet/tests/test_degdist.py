#!/usr/bin/env python
# coding: utf-8

"""Tests for the class DegreeDistribution."""

import cxnet
from cxnet import OUT, IN, ALL
import unittest

class DirectedNetwork(unittest.TestCase):
    "Tests for network degdist."

    def setUp(self):
        self.net = cxnet.Network.Formula("e->c, b->c->d, b->a, e->a, c->a, f->a, b->d, f->d,"
                "g->a, b->d, e->d, e->f")
        self.direction_dict =  {
                OUT: ("out", "OUT"),
                IN:  ("in", "IN"),
                ALL: ("", None),
            }
        self.known_values = {
            OUT: ([(1, 0.14285714285714285), (2, 0.2857142857142857), (3, 0.14285714285714285), (4, 0.14285714285714285)],
                2,
                [(1, 0.71428571428571419), (2, 0.5714285714285714), (3, 0.2857142857142857), (4, 0.14285714285714285)],
                (2.0332710672293155, 0.577616086377126)),
            IN: ([(1, 0.14285714285714285), (2, 0.14285714285714285), (4, 0.14285714285714285), (5, 0.14285714285714285)],
                3,
                [(1, 0.5714285714285714), (2, 0.42857142857142855), (4, 0.2857142857142857), (5, 0.14285714285714285)],
                (1.8132550920454504, 0.5421700613636337)),
            ALL: ([(1, 0.14285714285714285), (3, 0.2857142857142857), (4, 0.42857142857142855), (5, 0.14285714285714285)],
                0,
                [(1, 1.0), (3, 0.8571428571428571), (4, 0.5714285714285714), (5, 0.14285714285714285)],
                (1.753244074108329, 0.33214941610395754))
            }

    def test_directions(self):
        "The direction arguments should work correctly."
        for dircode in self.direction_dict:
            dd0 = cxnet.DegreeDistribution(self.net, mode=dircode)
            #print repr({dircode: (dd0.dd, dd0.n_0, dd0.cumulative_distribution(), dd0.exponent(k_min=1))})
            for direction in self.direction_dict[dircode]:
                dd = cxnet.DegreeDistribution(self.net, mode=direction)
                self.assertEqual(dd.direction, dircode)
                self.assertEqual(dd.dd, dd0.dd)

    def test_dd(self):
        "The dd values should be correct."
        for dircode in self.known_values:
            dd = cxnet.DegreeDistribution(self.net, mode=dircode)
            self.assertEqual(dd.dd, self.known_values[dircode][0])

    def test_n_0(self):
        "The number of zero-degree-nodes should be correct."
        for dircode in self.known_values:
            dd = cxnet.DegreeDistribution(self.net, mode=dircode)
            self.assertEqual(dd.n_0, self.known_values[dircode][1])

    def test_cumulative_distribution(self):
        "The cumulative_distribution should be correct."
        for dircode in self.known_values:
            dd = cxnet.DegreeDistribution(self.net, mode=dircode)
            self.assertEqual(dd.cumulative_distribution(), self.known_values[dircode][2])

    def test_cumulative_distribution(self):
        "The value and sigma of the exponent should be correct."
        for dircode in self.known_values:
            dd = cxnet.DegreeDistribution(self.net, mode=dircode)
            self.assertEqual(dd.exponent(k_min=1), self.known_values[dircode][3])

class Creation(unittest.TestCase):
    """Tests the creation of DegreeDistribution method."""

    # Test for success.
    def testdd(self):
        "dd should be the given list"
        dd = cxnet.DegreeDistribution([1,1,2,2,3])
        output = [(1,.4), (2,.4), (3,.2)]
        self.assertEqual(output, dd.dd)

    # Test for failure.
    def testBadDegreeList(self):
        "degree_list should not have float values"
        self.assertRaises(AssertionError, cxnet.DegreeDistribution, [1.1,1.1,2,2,3])
        self.assertRaises(AssertionError, cxnet.DegreeDistribution, [0.0,1.1,2,2,3])


# Test for success.
class DegdistlistMethod(unittest.TestCase):
    """Tests the degdistlist method."""

    input_output_pairs = [
            ([0,0,0,0],   [1]),
            ([1,0,1,0],   [.5, .5]),
            ([2,2,2,2],   [0, 0, 1]),
            ([1,2,3,4],   [0, .25, .25, .25, .25]),
            ([1,1,2,2,3], [0, .4, .4, .2]),
            ([2,1,2,3,1], [0, .4, .4, .2]),
            ]

    def testReturnValue(self):
        for input_, output in self.input_output_pairs:
            n = len(output)
            dd = cxnet.DegreeDistribution(input_)
            ddlist = dd.degdistlist()
            self.assertEqual(len(ddlist), n)
            for i in range(n):
                self.assertAlmostEqual(output[i], ddlist[i])


if __name__ == "__main__":
        unittest.main()
