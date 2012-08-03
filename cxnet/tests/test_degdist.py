#!/usr/bin/env python
# coding: utf-8

"""Tests for the class DegreeDistribution."""

import cxnet
import unittest

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
