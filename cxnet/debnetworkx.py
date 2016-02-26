from __future__ import with_statement
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import networkx
try:
    from .debnetworkc import CommonDebNetwork
except ImportError:
    print("""I could not import debnetworkc. Perhaps there is no apt module.
You can not create deb dependency network.""")

from .degdist import DegreeDistribution
# from time import strftime, gmtime
try:
    from platform import linux_distribution
except ImportError:
    linux_distribution = None


class Network(networkx.DiGraph):
    """Complex Network, NetworkX version

    Derived from the networkx.DiGraph class.
    Methods defined here start with "cx" to find them easier.

    """

    def summary(self):
        text = "%d nodes, %d edges, directed\n" % (
            self.number_of_nodes(), self.number_of_edges()
        )
        return text

    def cxneighborhood(self, pkg_name, plot=False, **kwargs):
        """Returns with the subgraph of successors, predecessors and the package itself.

        Parameters
        ----------
        pkg_name: string
            The name of the package.
        plot: boolean or string, default False
            If it is "pdf", the output will be a file like pkg_name.pdf.
            If other string, the output will be a file named in the string.
            If True, plot to the screen.
            If False, do not plot.

        """
        if pkg_name not in self:
            find = self.cxfind(pkg_name)
            if len(find) == 1:
                print("There is no package name %s.\n"
                      "I will use %s instead." %
                      (pkg_name, find[0]))
                pkg_name = find[0]
            else:
                print("There is no package name %s,\n"
                      "but the package names below include it.\n " % pkg_name,
                      "\n ".join(find))
                return []
        subgraph = networkx.ego_graph(self, pkg_name, undirected=1)

        if plot:
            node_color = kwargs.get("node_color", "skyblue")
            font_color = kwargs.get("font_color", "red")
            prog = kwargs.get("prog", "dot")
            networkx.draw_graphviz(
                subgraph,
                prog=prog,
                root=pkg_name,
                font_color=font_color,
                node_color=node_color)

        return subgraph

    def cxdegdist(self, **kwargs):
        """Returns with a DegreDistribution class analyzing and plotting distribution.

        Parameter
        ---------
        kwargs:
            parameters to the DegreeDistribution class
            Eg. direction {"in", "out", None}

        Returns
        -------
        dd: DegreeDistribution class object (see help(dd) )
        """
        return DegreeDistribution(self, **kwargs)

    def cxfind(self, namepart):
        """Returns the ordered list of package names containing the given part.

        Parameter
        ---------
        namepart: string
            A part of the package name.

        Returns
        -------
        names: ordered list of strings
            The ordered list of package names containing namepart.
        """
        names = [name for name in self if namepart in name]
        names.sort()
        return names


def read(name):
    """Reads deb-network from the gml-file written by igraph.
    """

    if not name.endswith("gml"):
        name = "{0}.gml".format(name)
    with open(name) as f:
        lines = f.readlines()
    newlines = []
    for line in lines:
        if line.strip().startswith("name"):
            newline = line.replace("name", "label", 1)
        else:
            newline = line
        newlines.append(newline)
    newname = "nx_{0}".format(name)
    with open(newname, "w") as f:
        f.writelines(newlines)
    network = networkx.read_gml(newname)
    # It should return a Network object instead of DiGraph
    return network


def debnetwork():
    cdn = CommonDebNetwork()
    if not cdn.has_purged_edges:
        cdn.purge_edges()
    print("Transforming to networkx.")
    debnet = Network()
    debnet.add_nodes_from(cdn.vertices)
    debnet.add_edges_from([(e[0], e[1]) for e in cdn.edges])
    debnet.sources_list = cdn.sources_list
    debnet.type = "networkx"
    return debnet
