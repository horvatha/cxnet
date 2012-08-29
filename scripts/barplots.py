#!/usr/bin/env python
# coding: utf-8

"""Plot the degree distribution as bar plots.
"""

import cxnet
import pylab

form = "{model} model, {binning} binning, {scales} scales"

def press(mesg="Press Enter"):
    raw_input(mesg)
    pylab.clf()

def BA_ER_plots():
    """Plot the degree distribution of two networks
    with several variation.
    """
    for net, model in [
                (cxnet.Network.Barabasi(10000, 2),"Barabasi-Albert"),
                (cxnet.Network.Erdos_Renyi(10000, .0032), "Erdos-Renyi")
            ][0:]:
        dd = net.cxdegdist()
        for binning in ["ondemand", "all", "log"]:
            dd.set_binning(binning)
            dd.bar_loglog()
            dd.loglog(markerfacecolor="gold", marker="d")
            pylab.legend()
            pylab.title(form.format(binning=binning, scales="loglog", model=model))
            press()
        dd.set_binning('ondemand')
        dd.bar_plot("log")
        pylab.title(form.format(binning="ondemand", scales="semilogx", model=model))
        press()
        dd.set_binning('ondemand')
        dd.bar_plot(yscale="log")
        pylab.title(form.format(binning="ondemand", scales="semilogy", model=model))
        press()
        dd.set_binning('ondemand')
        dd.bar_plot()
        pylab.title(form.format(binning="ondemand", scales="linlin", model=model))
        press()

def smallplot():
    "Plot a simple degree distribution with the three binning"
    dd = cxnet.DegreeDistribution([1,1,1,1,1,2,2,3,4,4,20,20,22])
    for binning in ["all", "ondemand", "log"]:
        dd.set_binning(binning)
        dd.bar_plot()
        pylab.title(form.format(binning=binning, scales="linlin", model="none"))
        press()

if __name__ == '__main__':
    BA_ER_plots()
    smallplot()
