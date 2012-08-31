#!/usr/bin/env python
# coding: utf-8

"""Tests for the module called tools."""

from cxnet.tools import average_values, decorator_generator, find_value
import unittest

class FindValue(unittest.TestCase):
    """Tests for find_value function."""

    def test_known_values(self):
        "find_value should return with the known values"
        known_values = (
                (("o", {"out":4}), 4),
                (("out", {"out":4, "outer":5}), 4),

            )
        for args, result in known_values:
            self.assertEqual(find_value(*args), result)

    def test_case_insensitivity(self):
        "find_value should neglect cases"
        known_values = (
                (("O", {"out":4}), 4),
                (("oUt", {"out":4}), 4),
                (("Out", {"out":4}), 4),
                (("OUT", {"out":4}), 4),

            )
        for args, result in known_values:
            self.assertEqual(find_value(*args), result)

    def test_bad_values(self):
        "find_value should rise exception in doubt"
        known_values = (
                ("q", {"out":4}),
                ("out", {"outest":4, "outer":5}),

            )
        for args in known_values:
            self.assertRaises(ValueError, find_value, *args)


IN, OUT, ALL, IG, BRM, BRMA, BRC = range(7)
values = {"in":IN, "out":OUT, "all":ALL,
          "ig":IG, "brm":BRM, "brma":BRMA, "brc":BRC}

directed  = decorator_generator("mode", values, 0)
directed1 = decorator_generator("mode", values, 1)

@directed
def decorated_function(mode):
    """helper function for the tests of decorator_generator"""
    return mode

@directed1
def decorated_function1(x, mode, y):
    """helper function for the tests of decorator_generator"""
    return mode

class DecoratorGenerator(unittest.TestCase):
    """Tests for decorator_generator function."""

    def test_case(self):
        "decorator_generator should be case insensitive"
        self.assertEqual(decorated_function(mode="out"), OUT)
        self.assertEqual(decorated_function(mode="oUt"), OUT)
        self.assertEqual(decorated_function(mode="Out"), OUT)
        self.assertEqual(decorated_function(mode="all"), ALL)
        self.assertEqual(decorated_function(mode="aLL"), ALL)
        self.assertEqual(decorated_function(mode="aLl"), ALL)

    def test_shorting(self):
        "decorator_generator should recognize abbreviated values"
        self.assertEqual(decorated_function(mode="o"), OUT)
        self.assertEqual(decorated_function(mode="O"), OUT)
        self.assertEqual(decorated_function(mode="OU"), OUT)
        self.assertEqual(decorated_function(mode="A"), ALL)
        self.assertEqual(decorated_function(mode="a"), ALL)
        self.assertEqual(decorated_function(mode="al"), ALL)


    def test_exact_values(self):
        "decorator_generator should recognize exact values even if it is a prefix"
        for key, value in values.iteritems():
            self.assertEqual(decorated_function(mode=key), value)

    def test_divers(self):
        "decorator_generator should raise exception if there are more possibilities"
        self.assertRaises(ValueError, decorated_function, mode="i")
        self.assertRaises(ValueError, decorated_function, mode="I")
        self.assertRaises(ValueError, decorated_function, mode="ar")

    def test_positional(self):
        """decorator_generator should work with positional arguments, it seems hard to solve"""
        self.assertEqual(decorated_function("out"), OUT)
        self.assertEqual(decorated_function1(0, "out", 0), OUT)

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
