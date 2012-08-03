import os
debug = False

# Set the graph_module.
cxnetrc=os.path.expanduser("~/.cxnetrc.py")
if os.path.isfile(cxnetrc):
    if debug:
        print """I have found an rc file: %s.""" % cxnetrc
    execfile(cxnetrc)
if "graph_module" not in dir():
    graph_module = "igraph"
    if debug:
        print """The graph_module was not set in the rc file. I try to use "igraph"."""
elif graph_module not in ["networkx", "igraph"]:
    raise ValueError("""The graph_module in the rc file is not correct. Choose "igraph" or "networkx", please.""")
else:
    print """The graph_module was set in the rc file to \"%s\".""" % graph_module


# Import useful things from the choosen module.
if graph_module == "igraph":
    try:
        from igraph import plot
    except ImportError:
        graph_module = False
        print """However the graph_module was set to "igraph", I can not import it."""
    else:
        if debug:
            print """I will use igraph. (It have been imported.)"""
        #from igraphtools import igraph_from_dot
        #from igraphtools import igraph_from_vertices_edges
        from debnetworki import debnetwork
        from debnetworki import Network
        from debnetworki import load_netdata
        import debnetworki
        from debnetworkc import TYPES
        from igraph import summary
        from igraph import Graph
        from igraph import WEAK, STRONG # for net.components
        from igraph import IN, OUT      # for net.degree

elif graph_module == "networkx":
    try:
        from networkx import diameter
    except ImportError:
        graph_module = False
        print """However the graph_module was set to "networkx", I can not import it."""
    else:
        if debug:
            print """I will use networkx. (It have been imported.)"""
        from networkx import barabasi_albert_graph, erdos_renyi_graph, complete_graph
        from networkx import connected_components, connected_component_subgraphs
        from networkx import Graph, DiGraph
        from debnetworkx import read
        from debnetworkx import debnetwork
        from debnetworkx import Network
        try:
            from networkx import draw
        except ImportError:
            pass


def indegree_changes(network1, network2, **kwargs):
    import pylab
    degree, delta_k = zip(*debnetworki.delta_k(network1, network2))
    pylab.loglog(degree, delta_k, "x")
    outfile = kwargs.get("outfile")
    if isinstance(outfile, str):
        pylab.savefig(outfile)
    pylab.show()

# If the choosen graph module can not be imported.
if graph_module is False:
    print """There is not graph module imported.
Without one of them cxnet has a very limited functionality.
You can try:
 - Fix the installation of the module.
 - Choose the another graph module.
   You can choose "igraph" or "networkx" in the rc file (~/.cxnetrc.py).
"""

# Some classes and functions useful for both graph modules.
from degdist import DegreeDistribution, split
from archives import get_netdata, put_debnetdata

if __name__ == "__main__":
    dn=debnetwork()
    dd=DegreeDistribution(dn)
    dn.summary()
