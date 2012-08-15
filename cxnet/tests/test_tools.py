#!/usr/bin/env python
# coding: utf-8

"""Tests for the module called tools."""

from cxnet.tools import average_values
import unittest

class AverageValues(unittest.TestCase):
    """Tests the average_values function."""

    # Test for success.
    def test_known_results(self):
        "The known result should agree."
        known_results = (
                ( ([], []), ((), ()) ),
                ( ([0,1,2], [1,5,2]), ((0,1,2), (1,5,2)) ),
                ( ([0,2,1], [1,5,2]), ((0,1,2), (1,2,5)) ),
                ( ([0,0,0], [0,1,2]), ((0,), (1,)) ),
                ( ([0,1,0], [0,1,2]), ((0,1), (1,1)) ),
                # float values
                ( ([0,1,0], [0.,1.,2.]), ((0,1), (1.,1.)) ),
                ( ([0,0,1,1], [0,1,2,3]), ((0,1), (.5, 2.5)) ),
                # negative values
                ( ([-1,-5,-1], [0,1,2]), ((-5, -1), (1,1)) ),
                # complex values
                ( ([0,0], [1-5j, 1+5j]), ((0,), (1,)) ),
                # with x_min
                ( ([0,1,1], [None,1,2], 1), ((1,), (1.5,)) ),
                ( ([0,1,2], [None,"a",2], 2), ((2,), (2,)) ),
                ( ([0,1,2], [0,1,2], 3), ((), ()) ),
                ( ([-1,2,-1], [1,1,0], 0), ((2,), (1,)) ),
            )
        for parameters, result in known_results:
            self.assertEqual(average_values(*parameters), result)

    def test_bad_parameters(self):
        "Bad parameters should raise exception."
        bad_parameters = (
            # non-integer in x
                ( ([.1, 2], [2, 1]),  "x values must be integers"),
                ( ([1.0, 2], [2, 1]),  "x values must be integers"),
                ( (["a", 1], [2, 1]),  "x values must be integers"),
                ( ([5j, 1], [2, 1]),  "x values must be integers"),
            # not equal length x and y
                ( ([0, 1, 2], [2, 1]),  "x and y must have the same length"),
            # not (int, float, complex) y value.
                ( ([0, 1, 2], "abc"),  "y values must contain integer, float and complex numbers"),
                ( ([0, 1], ["a", 2]),  "y values must contain integer, float and complex numbers"),
            # bad x_min value
                ( ([0, 1], [0, 2], 1j), "x_min must be integer, float or None"),
                ( ([0, 1], [0, 2], "a"), "x_min must be integer, float or None"),
            )
        for parameters, errortext in bad_parameters:
            self.assertRaisesRegexp(AssertionError, errortext, average_values, *parameters)


if __name__ == "__main__":
        unittest.main()
