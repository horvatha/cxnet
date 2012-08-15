#!/usr/bin/env python
# coding: utf-8

"""
The basic tools for the cxnet.

It does not imports the modules of cxnet just standard modules, numpy and
decorators.
"""

import collections
import contextlib
import os
import numpy
import decorators

OUT, IN, ALL = 1, 2, 3
WEAK, STRONG = 1, 2

#@decorators.trace
def average_values(x, y, x_min=None):
    """Return the average value for each x values.

    Parameters:
        x: sequence (list, tuple) of integers
            the x values
        y: sequence (list, tuple) of numbers, numbers must be integers, floats or complex
            the y values
        x_min: None, int or float
            the minimal x values to take into account

    Returns:
        (xx, yy) where xx are the sorted unique elements of x, and the yy values
        are the average (arithmetic mean) of the y values assigned to the same
        x values.

    Examples:
         >>> average_values([0, 0, 1, 1], [0, 1, 2, 3])
         ((0, 1), (0.5, 2.5))
         >>> average_values([0, 0, 1, 1, 2, 2], [0, 1, 2, 3, 4, 5], 1)
         ((1, 2), (2.5, 4.5))

    """
    assert x_min is None or isinstance(x_min, (int, float)), "x_min must be integer, float or None"
    assert len(x) == len(y), "x and y must have the same length"
    for xx in x:
        assert isinstance(xx, int), "x values must be integers"
    pairs = [(xx, yy) for xx, yy in zip(x, y) if xx >= x_min]
    for xx, yy in pairs:
        assert isinstance(yy, (int, float, complex)), "y values must contain integer, float and complex numbers"
    valuedict = collections.defaultdict(list)
    for xx, yy in pairs:
        valuedict[xx].append(yy)
    pairs = [(xx, numpy.average(valuedict[xx])) for xx in sorted(valuedict)]
    if not pairs:
        return ((), ())
    return tuple(zip(*pairs))

@contextlib.contextmanager
def working_directory(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)

@decorators.decorator
def direction(f):
    def _f(*args, **kwargs):
        if "direction" in kwargs:
            direction = kwargs["direction"]
            if direction in ["in", "IN"]:
                kwargs["direction"] = IN
            elif direction in ["out", "OUT"]:
                kwargs["direction"] = OUT
            elif direction in ["", "ALL", None]:
                kwargs["direction"] = ALL
            elif direction not in [IN, OUT, ALL]:
                raise ValueError("{0} is not a known direction.".format(direction))
        else:
                kwargs["direction"] = ALL
        f(*args, **kwargs)
    return _f

