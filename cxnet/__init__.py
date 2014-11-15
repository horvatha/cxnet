from __future__ import print_function
import os
debug = False

# Set the graph_module.
cxnetrc = os.path.expanduser("~/.cxnetrc.py")
if os.path.isfile(cxnetrc):
    if debug:
        print("""I have found an rc file: {0}.""".format(cxnetrc))
    execfile(cxnetrc)
if "graph_module" not in dir():
    graph_module = "igraph"
    if debug:
        print("""The graph_module was not set in the rc file. """
              """I try to use "igraph".""")
elif graph_module not in ["networkx", "igraph"]:
    raise ValueError("""The graph_module in the rc file is not correct. """
                     """Choose "igraph" or "networkx", please.""")
else:
    print("""The graph_module was set in the rc file to \"%s\"."""
          % graph_module)


# Import useful things from the choosen module.
if graph_module == "igraph":
    try:
        from igraph import plot  # noqa
    except ImportError:
        graph_module = False
        print("""However the graph_module was set to "igraph", """
              """I can not import it.""")
    else:
        if debug:
            print("""I will use igraph. (It have been imported.)""")
        # from igraphtools import igraph_from_dot
        # from igraphtools import igraph_from_vertices_edges
        from .debnetworki import debnetwork
        from .debnetworki import Network
        from .debnetworki import load_netdata  # noqa
        from cxnet import debnetworki
        from .debnetworkc import TYPES  # noqa
        from igraph import summary # noqa
        from igraph import Graph
        from igraph import WEAK, STRONG  # for net.components # noqa
        from igraph import OUT, IN, ALL  # for net.degree # noqa

elif graph_module == "networkx":
    try:
        from networkx import diameter  # noqa
    except ImportError:
        graph_module = False
        print("""However the graph_module was set to "networkx", """
              """I can not import it.""")
    else:
        if debug:
            print("""I will use networkx. (It have been imported.)""")
        from networkx import barabasi_albert_graph, erdos_renyi_graph  # noqa
        from networkx import complete_graph  # noqa
        from networkx import connected_components, connected_component_subgraphs  # noqa
        from networkx import Graph, DiGraph  # noqa
        from .debnetworkx import read  # noqa
        from .debnetworkx import debnetwork
        from .debnetworkx import Network  # noqa
        try:
            from networkx import draw  # noqa
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


def savepdf(fname, *args, **kwargs):
    """Saves the plot as pdf through eps file with epspdf command.

    The eps file will be kept as well.
    Sometimes the pdf output of the savefig is not good."""
    import matplotlib.pyplot as plt
    if fname.lower().endswith(".pdf"):
        fname0 = fname[:-4]
    else:
        fname0 = fname
    epsname = "{0}.eps".format(fname0)
    plt.savefig(epsname, *args, **kwargs)
    os.system("epspdf {0}".format(epsname))


def savefigs(fname0, *args, **kwargs):
    """Save figures into given formats.

    Input:
    - fname0: the name of the file without extension.
    - args: postional arguments. These arguments will be given to the savefig
      function.
    - kwargs: keyword arguments including the formats in the format given
      below. Other arguments will be given to the savefig function.

    Formats can be given with a space separated string of
    the formats below:
    - epspdf: it saves into pdf and eps. pdf format is created from
      eps with the epspdf command. It must be installed.
    - other formats: the formats that are known by the plt.savefig function.

    Example:

    We create the figure.eps, figure.pdf and figure.png files as:

    >>> savefigs("figure")

    We create the figure.png and figure.jpg files as:

    >>> savefigs("figure", formats="png jpg")

    """

    formats = kwargs.pop("formats", "epspdf png")
    if isinstance(formats, str):
        formats = formats.split()
    for format in formats:
        if format == "epspdf":
            savepdf(fname0, *args, **kwargs)
        else:
            import matplotlib.pyplot as plt
            fname = "{0}.{1}".format(fname0, format)
            plt.savefig(fname, *args, **kwargs)

# If the choosen graph module can not be imported.
if graph_module is False:
    print("""There is not graph module imported.
Without one of them cxnet has a very limited functionality.
You can try:
 - Fix the installation of the module.
 - Choose the another graph module.
   You can choose "igraph" or "networkx" in the rc file (~/.cxnetrc.py).
""")

# Some classes and functions useful for both graph modules.
from .degdist import DegreeDistribution, split  # noqa
from .archives import get_netdata, put_debnetdata  # noqa
from .tools import vertex_colors  # noqa

if __name__ == "__main__":
    dn = debnetwork()
    dd = DegreeDistribution(dn)
    dn.summary()
