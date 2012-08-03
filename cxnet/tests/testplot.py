#!/usr/bin/env python
# coding: utf-8

"""Test for plotting with cxnet."""

import cxnet
import unittest
import pylab


def example_network(named=True, directed=True,
                bigger=True, with_accent=False):
    """Returns with an example network optionally with long names.

    Parameters:
        - named: boolean
            The net.vs needs to have 'name' attribute or not.
        - directed: boolean
            Whether the network need to be directed or not.
        - bigger: boolean
            There is two variants with less or more edges,
            if bigger is True, the bigger will be created.

    """
    net = cxnet.Network(directed=directed)
    if with_accent:
        vertices = """alma kutyamutya donald_duck ouagadougou Arbeitslosenunterstützung Adeva_Kedavra Massimiliano_Robespierr Pablo_Diego_Francesco_Trinidad_Ruizzi_Picasso kalamajkakeverő""".split()
    else:
        vertices = """alma kutyamutya donald_duck ouagadougou Arbeitslosenunterstutzung Adeva_Kedavra Massimiliano_Robespierr Pablo_Diego_Francesco_Trinidad_Ruizzi_Picasso kalamajkakevero""".split()
    net.add_vertices(len(vertices))
    if named:
        net.vs["name"] = vertices
    edges = [(0, 7), (1, 2), (0, 6), (0, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), ]
    if bigger:
        edges.extend([(i,7) for i in range(3,7)])
    net.add_edges(edges)
    return net

def plot_with_networkx(target=None,
        named=True, bigger=False,
        layout=None, show=True,
        **kwargs):
    """Plots a Network with networkx."""
    net = example_network(named=named, directed=True, bigger=bigger)
    net.plot_with_networkx(layout=layout, **kwargs)
    if isinstance(target, str):
        pylab.savefig(target)
    elif target is not None:
        raise ValueError("target must be string or None.")
    if show:
        pylab.show()


class NetworkXPlot(unittest.TestCase):
    """Tests cxnet's plotting possibilities based on NetworkX."""

    def test_nx_plots(self):
        """Plot some variants of the same netwo"""
        for named in [True, False]:
            for layout in "circular spring".split():
                target = "nxplot_{0}{1}.png".format("named_" if named else "", layout)
                fig = pylab.figure()
                plot_with_networkx(target, named=named, layout=layout, show=False)
        print("See nxplot*.pdf .")


class IgraphPlot(unittest.TestCase):
    """Tests cxnet's plotting possibilities based on igraph."""

    def test_plot_neighborhood(self):
        """Plots neighborhoods with Igraph"""
        pkg_names="vim nautilus python-apt python-cairo python3".split()
        dn = cxnet.debnetwork()
        for pkg_name in pkg_names:
            dn.cxneighborhood(pkg_name, plot="pdf")
        print("See neighbors_*.pdf .")

    def test_plotexample(self):
        """Plots the variants of the example network."""
        for directed in (True, False):
            net = example_network(directed=directed, bigger=True)
            for full in (True, False):
                if full:
                    target = "example_plot_{0}.png".format(
                            "directed" if directed else "undirected"
                            )
                    net.plot(target)
                else:
                    net.cxneighborhood("donald_duck", plot="pdf")

if __name__ == "__main__":
        unittest.main()
