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
from cxnet import decorators
import inspect

OUT, IN, ALL = 1, 2, 3
WEAK, STRONG = 1, 2
vertex_colors = [
    'blue', 'fuchsia', 'aqua', 'grey', 'maroon', 'olive',
    'yellow', 'teal', 'navy', 'green', 'white', 'silver', 'red', 'lime',
    'orange', 'pink', 'gold']


# @decorators.trace
def average_values(x, y, x_min=float("-inf")):
    """Return the average value for each x values.

    Parameters:
        x: sequence (list, tuple) of integers
            the x values
        y: sequence (list, tuple) of numbers, numbers must be integers,
            floats or complex the y values
        x_min: int or float
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
    assert x_min is None or isinstance(x_min, (int, float)),\
        "x_min must be integer, float or None"
    assert len(x) == len(y), "x and y must have the same length"
    for xx in x:
        assert isinstance(xx, int), "x values must be integers"
    pairs = [(xx, yy) for xx, yy in zip(x, y) if xx >= x_min]
    for xx, yy in pairs:
        assert isinstance(yy, (int, float, complex)),\
            "y values must contain integer, float and complex numbers"
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
def direction_old(f):
    def _f(*args, **kwargs):
        if "mode" in kwargs:
            mode = kwargs["mode"]
            if mode in ["in", "IN"]:
                kwargs["mode"] = IN
            elif mode in ["out", "OUT"]:
                kwargs["mode"] = OUT
            elif mode in ["", "ALL", None]:
                kwargs["mode"] = ALL
            elif mode not in [IN, OUT, ALL]:
                raise ValueError("{0} is not a known mode.".format(mode))
        else:
                kwargs["mode"] = ALL
        f(*args, **kwargs)
    return _f


class StandardValue(object):
    def __init__(self, values, default=None):
        for key in values:
            assert key.islower(),\
                "The keys of values must be lower case strings."
        self.values = values
        assert default in values.values() or default is None,\
            "default must be in values.values() of must be None."
        self.default = default

    def get(self, value):
        if value in self.values.values():
            return value
        if value is None:
            if self.default is not None:
                    return self.default
            else:
                raise ValueError(
                    "It the value is None, there must be a default value.")
        assert isinstance(value, str),\
            "value must be None | string | a value of values.values()."
        value = value.lower()
        if value in self.values:
            return self.values[value]
        possibilities = set(
            val for val in self.values if val.startswith(value))
        if len(possibilities) == 1:
            return self.values[possibilities.pop()]
        elif len(possibilities) == 0:
            raise ValueError(
                "Not any possibility for '{0}'.".format(value)
                )
        else:
            raise ValueError(
                "More then one possibilities for '{0}'.".format(value)
                )


def default_value(function, argument):
    argspec = inspect.getargspec(function)
    defaults = argspec.defaults
    default_args = dict(zip(argspec.args[-len(defaults):], defaults))
    return default_args[argument]


def decorator_generator(param, values, default=None):
    """Returns with a decorator for easier string parameter.

    With this decorator the string parameters can be abbreviated.

    Parameters:
        param: string
            the parameter we want abbreviate
        values: dict
            the values to substitute
        default:
            the default value for the parameter

    Example:

        >>> word = decorator_generator("word",
                                       {"in":"in", "out":"aus", "ill":"Krank"})
        >>> @word
        ... def translate(word):
        ...     return word
        ...
        >>> translate("o")
        "aus"
        >>> translate(word="o")
        "aus"
        >>> translate("oUt")
        "aus"
        >>> translate("il")
        "Krank"
        >>> translate("i")
        ValueError: ...
    """
    standard_value = StandardValue(values, default)

    @decorators.decorator
    def decorator(fn):
        def _newfn(*args, **kwargs):
            if param in kwargs:
                kwargs[param] = standard_value.get(kwargs[param])
                return fn(*args, **kwargs)
            argspec = inspect.getargspec(fn)
            if param in argspec.args:
                position = argspec.args.index(param)
                if len(args) > position:
                    args = list(args)
                    args[position] = standard_value.get(args[position])
                else:
                    kwargs[param] = standard_value.get(default_value(fn, param))
            else:
                kwargs[param] = standard_value.default
            return fn(*args, **kwargs)
        return _newfn
    return decorator

directions = {"out": OUT, "in": IN, "all": ALL}
direction = decorator_generator("mode", directions, default=ALL)
