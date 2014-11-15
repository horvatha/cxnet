#!/usr/bin/env python
# coding: utf-8

import pylab


def plot(exponent, xmax, xmin=1, coeff=1, num=1000,
         variable_name="k", **kwargs):
    """Plot power-law function.

    The format of the function is:
    x    ->    coeff * x**exponent
    (** is the exponentiation operation, 2**3 = 2*2*2)

    Parameters:
        exponent: float or int
            the exponent of the power-law function
        xmax: int
            the maximal value of x
        xmin: int
            the minimal value of x
        coeff: float or int
            the co-efficient of the power-law function
        num: int > 1
            the number of points
        kwargs: the keyword argumentums to pass to the plot function
            see the pylab.plot function
    """
    assert xmin < xmax, "xmax must be greater then xmin"
    assert num > 1, "at least two point need to plot: num > 1"
    x = pylab.linspace(xmin, xmax, num)
    if "linestyle" not in kwargs:
        kwargs["linestyle"] = "--"
    assert isinstance(variable_name, str), "the variable_name must be string"
    assert isinstance(coeff, (float, int)), "the coeff must be integer or float"
    assert isinstance(exponent, (float, int)),\
        "the exponent must be integer or float"
    if "label" not in kwargs:
        coeff_tex = "" if coeff == 1 else r"{0:.3f}\times ".format(coeff)
        kwargs["label"] = r"${1}\mapsto {0}{1}^{{{2:.3f}}}$".format(
            coeff_tex, variable_name, exponent
        )
    return pylab.plot(x, coeff * x**exponent, **kwargs)
