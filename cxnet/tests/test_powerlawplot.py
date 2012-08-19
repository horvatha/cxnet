#!/usr/bin/env python
# coding: utf-8

"""Test for plotting with power-law."""

import cxnet
import unittest
import pylab



class WithPowerlaw(unittest.TestCase):
    """Tests with_powerlaw parameters.."""

    def setUp(self):
        self.net = cxnet.Network.Barabasi(10000, 4, directed=True)

    def test_clutering_degree_plot(self):
        """Plots clustering degree plot with power-law."""
        pylab.clf()
        self.net.cxclustering_degree_plot()
        pylab.savefig("clustering_degree.pdf")
        pylab.clf()
        self.net.cxclustering_degree_plot(direction="in")
        pylab.savefig("clustering_indegree.pdf")

    def test_clutering_degree_plot_linestyle(self):
        "powerlaw should be plotted with proper linestyle"
        pylab.clf()
        self.net.cxclustering_degree_plot(powerlaw_linestyle=":")
        pylab.savefig("clustering_degree_linestyle.pdf")

    def test_clutering_degree_plot_marker(self):
        "powerlaw should be plotted with proper marker"
        pylab.clf()
        self.net.cxclustering_degree_plot(powerlaw_marker="x")
        pylab.savefig("clustering_degree_marker.pdf")

    def test_bad_args(self):
        "bad argument should raise Exeption"
        self.assertRaises(AssertionError, self.net.cxclustering_degree_plot,
                "in")

if __name__ == "__main__":
        unittest.main()
