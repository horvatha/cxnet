#!/usr/bin/env python
# coding: utf-8
from __future__ import division
from __future__ import print_function

try:
    import gettext
    transl = gettext.translation("packages", "/home/ha/cxnet/locale")
    # transl = gettext.translation("packages", "/usr/share/locale") # If I can put into this library.
    _ = transl.ugettext
except ImportError:
    _ = lambda str: str
except IOError:
    _ = lambda str: str

from math import log, sqrt
try:
    import pylab
except (ImportError, RuntimeError):
    pylab_module = False
else:
    pylab_module = True

import numpy

import sys
from cxnet import tools
from .tools import OUT, IN, ALL
from cxnet import powerlaw

#split = lambda tl: ([x for x, y in tl], [y for x, y in tl])
split = lambda List: zip(*List)

def logarithmic_binning(dd, l=1, mult=2):
    if not isinstance(dd[0], tuple):
        dd = [(i, dd[i]) for i in range(len(dd)) if dd[i] != 0]
    n = dd[-1][0]
    start, stop = 1, l+1
    ebin = []
    division_points = [start]
    while start < n:
        summa = sum( p for k, p in dd if start<= k < stop )
        ebin.append(summa/(stop-start))
        division_points.append(stop)
        l = l*mult
        start=stop
        stop = stop+l
    return ebin, division_points

class DegreeDistribution:
    """Make, analyze and plot the degree distribution.

    Parameters:
      `network_or_degree_list`:
         the investigated network (NetworkX or IGraph)
         or the list of degrees or the dict of the form {vertex:degree}.
      `mode`: "in", "out", None [default]
         the direction of the connection to count.
         If None, plain degree will be used.
      `binning`: None, "all", "ondemand", "log" or "logarithmic"
         See at set_binning method.

    some variables:

    - `dd`: the degree distribution az a pair of (k, p_k) values
    - `dd_smeared`: as the dd, but with bin smearing
    - `max_deg`: maximum of degree
    - `number_of_vertices`: the number of vertices in the network
    - `n_0`: the number of vertices with zero degree

    more important functions:

    - `summary`: Write informations to screen or file about the distribution.
    - `plot, loglog, semilogy, errorbar`: Plotting functions as in pylab.
    - `bin_smearing`: Return the bin smeared distribution.
    - `set_binning`: Set the type of the binning.
    - `cumulative_plot`: Plots the cumulative distribution.
    """

    @tools.direction
    def __init__(self, network_or_degree_list, verbose=True, **kwargs):
        """
        """

        self.verbose=verbose

        self.kwargs = kwargs
        self.gamma = None # The absolute value of exponent

        self.direction = kwargs.pop("mode")

        # Argument can be a network or a degree list.
        # We create degree list self.deg
        if isinstance(network_or_degree_list, (tuple, list, dict)):
            self.deg = network_or_degree_list
            for d in self.deg:
                assert isinstance(d, int) and d >= 0
            network = None
        else:
            network = network_or_degree_list
            # We can use NetworkX or IGraph modules.
            if "adj" in dir(network): # NetworkX
                self.deg = {
                        IN: network.in_degree(),
                        OUT: network.out_degree(),
                        ALL: network.degree()
                    }[self.direction]
            else:
                self.deg = {
                        IN: network.indegree(),
                        OUT: network.outdegree(),
                        ALL: network.degree()
                    }[self.direction]

        if isinstance(self.deg, dict):
            self.deg = self.deg.values()

        self.index, self.texindex, self.degree_type = {
                ALL: ("",     "",       "plain degree"),
                IN:  ("_in",  "_{in}",  "in-degree"),
                OUT: ("_out", "_{out}", "out-degree"),
            }[self.direction]

        self.max_deg = max(self.deg)

        self.dd0=[(i, j) for i, j in enumerate(numpy.bincount(self.deg))]
        self.n_0 = self.dd0[0][1]
        self.dd0=[(i, j) for i, j in self.dd0 if i > 0 and j > 0]
        self.number_of_vertices = len(self.deg)
        self.dd=[(i, j/self.number_of_vertices) for i, j in self.dd0]

        self.binning = kwargs.pop("binning", None)
        if self.binning is not None:
            self.bin_smearing()
        self.labelfontsize=15
        if kwargs:
            raise ValueError("kwargs must not have key(s): {0}".format(", ".join(kwargs.keys())))

    def cumulative_distribution(self):
        """Return the cumulative degree distribution

        The distribution is a list of (k, P(>k)) pairs.
        """

        cum_dd = []
        sum_p = 0
        for k, p in reversed(self.dd):
            sum_p += p
            cum_dd.append((k, sum_p))
        return list(reversed(cum_dd))

    def cumulative_plot(self, with_powerlaw=False, **kwargs):
        """Plot the cumulative distribution.

        Parameter:
            with_powerlaw: boolean
                Whether to plot the calculated powerlaw as well or not.
            """
        x,y = split(self.cumulative_distribution())
        if "label" not in kwargs:
            kwargs["label"] = "$P(k%s)$" % self.texindex
        p = pylab.loglog(x,y, **kwargs)
        pylab.xlabel("$k%s$" % self.texindex, fontsize=self.labelfontsize)
        pylab.ylabel("$P(k%s)$" % self.texindex, fontsize=self.labelfontsize)
        pylab.title("Cumulative %s distribution" % self.degree_type)
        if with_powerlaw:
            kwargs.pop("marker", None)
            kwargs.pop("label", None)
            if self.gamma is None:
                self.exponent()
            powerlaw.plot(exponent=-self.gamma + 1,
                    xmax=self.max_deg, xmin=self.k_min,
                    num=2,
                    **kwargs
                    )
        return p

    def exponent(self, k_min=5.5):
        """Return with exponent and sigma of exponent.

        Parameters:
         k_min: float or integer, k_min>0
           the minimal degree in the equation referenced below

        The exponent end error are caculated with the equations written in [1]
        page 4.

        ::

         [1]
         @article{newman-2005-46,
           url = {http://arxiv.org/abs/cond-mat/0412004},
           author = {M.~E.~J. Newman},
           title = {Power laws, Pareto distributions and Zipf's law},
           journal = {Contemporary Physics},
           volume = {46},
           pages = {323},
           year = {2005},
         }

         [2]
         @misc{clauset-2007,
           url = {http://arxiv.org/abs/0706.1062},
           author = {Aaron Clauset and Cosma Rohilla Shalizi and M.~E.~J. Newman},
           title = {Power-law distributions in empirical data},
           year = {2007}
         }

        """

        assert isinstance(k_min, (float, int)) and k_min > 0
        deg = [k for k in self.deg if k > k_min]
        summa = sum(map(lambda x: log(x/k_min), deg))
        n = len(deg)
        gamma = 1 + n/summa
        sigma = sqrt(n+1) / summa

        self.gamma = gamma
        self.k_min = k_min

        return gamma, sigma

    def exponent_plot(self, k_mins=None, file="output.pdf"):
        """Plot the calculated exponents for several k_mins.

        Parameters:
        - `k_mins` [optional, default None]: list of the k_mins or None
            for all of the k_min in the list k_mins calculate the exponent
            and the sigma and plot it.
        - `file` [optional, default "output.pdf"]:
            the file for saving the plot
        """
        if k_mins == None:
            step = int(self.max_deg/20) if self.max_deg>20 else 1
            k_mins = range(1,self.max_deg,step)

        K=[]
        G=[]
        S=[]
        for k in k_mins:
            k_min = k - 0.5
            g,s = self.exponent(k_min)
            result =  "k_min=%.1f: %f+-%f" % (k,g,s)
            print(result)
            K.append(k)
            G.append(g)
            S.append(s)
        print("%f <= gamma%s <= %f" % (min(G), self.index, max(G)))
        p = pylab.errorbar(K, G, yerr=S)
        pylab.xlabel("k_min")
        pylab.ylabel("gamma%s" % self.index)
        pylab.title("The dependence from k_min of the exponent (%s)" % \
                self.degree_type)
        #pylab.gca().set_yscale("log")
        #pylab.gca().set_xscale("log")
        pylab.savefig(file)
        pylab.show()
        return p

    def plot_powerlaw(self, **kwargs):
        """Plot a power-law function with exponent self.gamma.

        Parameters:
            kwargs:
                Keyword argumentums are forwarded to the plot function.

        Return with the plot.
        """

        if self.gamma is None:
            self.exponent()
        p = powerlaw.plot(exponent=-self.gamma,
                xmax=self.max_deg, xmin=self.k_min,
                **kwargs
                )
        pylab.show()
        return p

    binning_warning = """You need to run dd.set_binning(b) first.
Examples:
    dd.set_binning()
    dd.set_binning('all')
    dd.set_binning('log')
    dd.set_binning('ondemand')
if your DegreeDistribution object is called dd.
The result of the first two examples are the same.
"""


    def plot(self, plot=None, with_powerlaw=False, **kwargs):
        """Plot the bin smeared degree distribution.

        """

        """
        There was an input earlier
          intervals: list of pairs of (min, max)
          fitted point are where min <= degree <= max.
          If you want to fit the whole, set min to 0 and
          max to bigger than the greatest degree.
          In this case fitting is from the smallest non zero
          degree to the largest degree.
        """

        try:
            dd = self.dd_smeared
        except AttributeError:
            print(self.binning_warning)
            return
        if plot is None:
            plot=pylab.plot
        _, _, x, y = split(dd)
        x=pylab.array(x)
        if "label" not in kwargs:
            kwargs["label"] = "$p(k{0})$, {1} binned".format(
                                        self.texindex, self.binning)
        p = plot(x,y,".", **kwargs)
        pylab.xlabel("$k%s$" % self.texindex, fontsize=self.labelfontsize)
        pylab.ylabel("$p(k%s)$" % self.texindex, fontsize=self.labelfontsize)
        title = "%s distribution" % self.degree_type
        pylab.title(title.capitalize())
        if with_powerlaw:
            for arg in ["marker", "label"]:
                kwargs.pop(arg, None)
            self.plot_powerlaw(**kwargs)
        pylab.show()
        return p

    def loglog(self, **kwargs):
        """Plot the bin smeared degree distribution
        with loglog scales (log scale in each axes).

        """
        return self.plot(plot=pylab.loglog, **kwargs)

    def semilogy(self, **kwargs):
        """Plot the bin smeared degree distribution
        with semilogy scales (log scale in y axis).

        """
        return self.plot(plot=pylab.semilogy, **kwargs)

    def errorbar(self, **kwargs):
        """Plot the degree distribution with error bars.

        """

        try:
            dd = self.dd_smeared
        except AttributeError:
            print(self.binning_warning)
            return

        if "label" not in kwargs:
            kwargs["label"] = "$p(k{0})$, {1} binned".format(
                                        self.texindex, self.binning)
        if "marker" not in kwargs:
            kwargs["marker"] = ""

        x_low, x_high, x, height = split(dd)
        xerr_r = [ (x_low[i] - x[i]) for i in range(len(dd)) ]
        xerr_l = [ (x[i] - x_high[i])  for i in range(len(dd)) ]
        p = pylab.errorbar(x,y,xerr=[xerr_l, xerr_r], fmt=".", **kwargs)
        pylab.gca().set_yscale("log")
        pylab.gca().set_xscale("log")

        pylab.show()
        return p

    def bar_plot(self, xscale="linear", yscale="linear", **kwargs):
        """Plot the degree distribution with bars.

        Parameters:
            xscale: "linear" or "log"
            yscale: "linear" or "log"
            with_marker: boolean
                Plots with marker as well.
        """

        try:
            dd = self.dd_smeared
        except AttributeError:
            print(self.binning_warning)
            return
        with_marker = kwargs.pop("with_marker", False)
        with_powerlaw = kwargs.pop("with_powerlaw", False)

        if "label" not in kwargs:
            kwargs["label"] = "$p(k{0})$, {1} binned".format(
                                        self.texindex, self.binning)
        x_low, x_high, x, y = split(dd)
        width = [xh - xl for xl, xh, _, _ in dd]
        if yscale == "log":
            y_min = min(yy for yy in y if yy > 0)
            bottom = 10**numpy.floor(numpy.log10(y_min/1.02))
            height = [yy - bottom if yy > 0 else 0 for yy in y]
        else:
            bottom = 0
            height = y
        p = pylab.bar(x_low, height, width,
                bottom=bottom,
                **kwargs)
        pylab.gca().set_yscale(yscale)
        pylab.gca().set_xscale(xscale)
        kwargs["markerfacecolor"] = kwargs.get("markerfacecolor", "gold")
        kwargs["marker"] = kwargs.get("marker", "D")
        if with_marker:
            self.plot(**kwargs)

        if with_powerlaw:
            for arg in ["marker", "label", "markerfacecolor"]:
                kwargs.pop(arg, None)
            kwargs["color"] = "red"
            self.plot_powerlaw(**kwargs)

        pylab.show()
        return p

    def bar_loglog(self, **kwargs):
        "As bar_plot, but with logarithmic scales as default."
        return self.bar_plot(xscale="log", yscale="log", **kwargs)

    def summary(self, verbosity=0, file=None):
        """Write informations to screen or file about the distribution.

        Parameters:

          file: if string, it will be the name of the file,
                if None (default), it will write to screen (stdout).
          verbosity: integer (0,1,2), default 0
                The bigger the value is, the more information you get.
        """

        if type(file) == type(""):
            f=open(file, "w")
        else: f= sys.stdout

        f.write(_("The number of vertices is %d. ") % self.number_of_vertices)
        f.write(_("The largest %s is %d.\n") % (self.degree_type, self.max_deg))
        f.write("\nDegree distribution:\n")
        f.write(_("     0:%7.4f%%\n") % \
            (self.n_0/self.number_of_vertices*100))

        column=1
        for degree, probability in self.dd:
            f.write(" %5d:%7.4f%%" % (degree, probability*100))
            if column == 5:
                f.write("\n")
                column=1
            else: column += 1
        f.write("\n")

    def bin_smearing(self):
        """Calculates the binned distribution."""
        abscissa, ordinate = split(self.dd)
        x = abscissa
        if self.binning in ["all", None]:
            dd_smeared = [(x-.5, x+.5, x, y) for x, y in self.dd]
            self.binning = "all"
        elif self.binning in ["log", "logarithmic"]:
            # borders like 1,2,4,8,16
            probabilities, division_points = logarithmic_binning(self.dd, l=1, mult=2)
            mean_degrees = [sqrt(division_points[i]*division_points[i+1])
                              for i in range(len(probabilities))]
            dd_smeared =  zip(division_points[:-1], division_points[1:], mean_degrees, probabilities)
        elif self.binning == "ondemand":
            if len(self.dd) == 1:
                dd_smeared = self.dd
            else:
                inner_division_points = [sqrt(x[i] * x[i+1])
                        for i in range(len(self.dd) - 1)]
                first_division_point = x[0]**2 / inner_division_points[0]
                last_division_point =  x[-1]**2 / inner_division_points[-1]
                division_points = [first_division_point] + \
                    inner_division_points + \
                    [last_division_point]
                dd_smeared = [
                    (division_points[i],
                     division_points[i+1],
                     self.dd[i][0],
                     self.dd[i][1] /
                          (division_points[i+1] - division_points[i])
                    )
                    for i in range(len(self.dd))
                    ]
        else:
            print("There is no binning called '%s'" % self.binning)
            return

        self.dd_smeared = dd_smeared
        return dd_smeared

    def set_binning(self, binning=None):
        """Sets the type of binning, and calculates the binned distribution."""
        if binning is not None and binning == self.binning:
            return
        self.binning = binning
        self.bin_smearing()

#TODO I think it is half-ready.
class PowerLawDistribution:
    """Return a power-law distribution.

    Parameters:
    - `gamma`: the absolute value of the exponent.
    - `xmin`
    - `error`

    Method:
        cumulative_distribution()
    """

    def __init__(self, gamma, xmin=1, error=1e-5):
        self.gamma = gamma
        self.xmin = xmin
        self.error = error
        x = numpy.exp(-numpy.log(error)/gamma)
        xmax = int(x+1)
        zeta = 0.0
        cumdist = []
        for i in reversed(range(xmin, xmax+1)):
            value = i ** (-gamma)
            zeta += value
            cumdist.append([i, zeta])
        for i in range(len(cumdist)):
            cumdist[i][1] /= zeta
        self.cumdist = cumdist
        self.zeta = zeta

    def cumulative_distribution(self):
        return self.cumdist

def KolmogorovSmirnoff_statistics(dd1, dd2):
    """Return the Kolmogorov-Smirnoff statistic"""
    cum1 = dd1.cumulative_distribution()
    cum2 = dd2.cumulative_distribution()
    minimum = max(cum1[0][0],  cum2[0][0])
    maximum = max(cum1[-1][0], cum2[-1][0])
    index1 = len(cum1) - 1
    index2 = len(cum2) - 1
    summa1 = summa2 = 0

    difference = 0
    for i in reversed(range(minimum, maximum+1)):
        if cum1[index1][0] == i:
            summa1 = cum1[index1][1]
            index1 -= 1
        if cum2[index2][0] == i:
            summa2 = cum2[index2][1]
            index2 -= 1
        if abs(summa1 - summa2) > difference:
            difference = abs(summa1 - summa2)
    return difference

if __name__ == "__main__":
    import igraph
    g = igraph.Graph.Barabasi(10000, 4)
    dd = DegreeDistribution(g)
    dd.summary()
    # dd.summary("info.txt")
    print(dd.exponent())
    dd.cumulative_plot(with_powerlaw=True)
    pylab.legend()
    pylab.savefig("tmp_cumulative.png")

    pylab.clf()
    dd = DegreeDistribution(g)
    dd.set_binning("all")
    dd.loglog(marker="x")
    dd.set_binning("ondemand")
    dd.loglog(marker="+")
    dd.set_binning("log")
    dd.loglog(with_powerlaw=True, marker="d")
    pylab.legend()
    pylab.savefig("tmp_degdist.png")

    pylab.clf()
    dd = DegreeDistribution(g, mode=OUT)
    dd.set_binning("log")
    dd.loglog(with_powerlaw=True, marker="d")
    pylab.legend()
    pylab.savefig("tmp_outdegdist.png")
