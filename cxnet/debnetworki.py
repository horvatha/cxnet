#!/usr/bin/env python
# coding: utf-8

from __future__ import with_statement
from __future__ import division
from __future__ import print_function
from functools import reduce

import math
import igraph
try:
    from .debnetworkc import CommonDebNetwork
except ImportError:
    print("""I could not import debnetworkc. Perhaps there is no apt module.
You can not create deb dependency network.""")
else:
    from .debnetworkc import PkgInfo
    from .debnetworkc import TYPES
from .archives import get_netdata, put_debnetdata, get_archive_name

from .degdist import DegreeDistribution
from time import strftime, gmtime
# from os.path import getatime
import os
import operator
try:
    from platform import linux_distribution
except ImportError:
    linux_distribution = None
import platform
import pylab
from .tools import OUT, IN, ALL
from .tools import direction, average_values
from .powerlaw import plot as powerlaw_plot


class Network(igraph.Graph):
    """Complex Network, Igraph version

    Derived from the igraph.Graph class.
    Methods defined here start with "cx" to find them easier.

    It includes the plot function as well.

    """

    def plot(self, target=None, labels=True, **kwargs):
        """It is almost same az igraph.plot().

        But it has not a graph argument, and left and right margins are wider
        by default, and edges are orange if there are vertex labels.

        Parameter:
            target: string or None
                As in igraph.plot.
            labels: list or boolean
                If it is a list, it will passed to the vs["label"].
                If it is true, and no "label" attribute, but there is
                "name" attribute, the "name" will passed to "label".

        """
        if not kwargs.get("layout"):
            kwargs["layout"] = self.layout_kamada_kawai()
        if kwargs.get("margin") is None:
            kwargs["margin"] = (70, 5) * 2

        attributes = self.vs.attributes()
        if isinstance(labels, list):
            self.vs["label"] = labels
        elif labels and "label" not in attributes and "name" in attributes:
            self.vs["label"] = self.vs["name"]
        igraph.plot(self, target, **kwargs)

    @direction
    def cxlargest_degrees(self, mode=ALL, limit=None, print_it=False):
        """Returns with the vertices with the largest degrees.

        Parameters:
            mode: "out", "in", "all" (or OUT, IN, ALL)
                It uses out-degree, in-degree or (plain) degree
                respectively. Default is all.

            limit: integer or None, default None
               Only the packages with the degree < limit will listed.

               If None, a limit will be set
               (good for debian package dependency network):

               - plain: 500
               - in: 300
               - out: 50

            print_it: boolean
                Print the result in a pretty way.

        Returns:
            hd: a list of pairs of (degree, package name)

        Example::

            cn.cxlargest_degree(direction='in', limit=500)

        """

        assert mode in [OUT, IN, ALL], 'mode argument must be OUT, IN or ALL.'
        if mode is ALL:
            if limit is None:
                limit = 500
            vs = self.vs(_degree_ge=limit)
            degree = self.degree
        elif mode == IN:
            if limit is None:
                limit = 300
            vs = self.vs(_indegree_ge=limit)
            degree = self.indegree
        elif mode == OUT:
            if limit is None:
                limit = 50
            vs = self.vs(_outdegree_ge=limit)
            degree = self.outdegree
        list_ = [(degree(v), v["name"]) for v in vs]
        list_.sort(reverse=True)

        lines = ["%6d %-20s\n" % pair for pair in list_]
        lines.append("Degree limit: {}\n".format(limit))
        if print_it:
            for line in lines:
                print(line[:-1])  # \n not printed
        with open("largest_%sdegree.txt" %
                  {OUT: "out-", IN: "in-", ALL: ""}[mode], "w") as f:
            f.writelines(lines)
        return list_

    def cxneighbors(self, pkg_name):
        """Returns with the successors and predecessors ("out and inneighbors")
        if it is a directed networks. Neighbors otherwise.

        Parameters:
            pkg_name: string
                The name of the package.
                (You can find it with the cxfind method.)

        Returns:
            In a directed network
                returns a tuple of (predecessors, successors) where

                - predecessors are list of neighbors on incoming edges,
                - successors are list of neighbors on outcoming edges.
            In an undirected network
                returns a tuple of (neighbors, None) where
                neighbors are list of neighbors.

        """

        if pkg_name not in self.vs["name"]:
            find = self.cxfind(pkg_name)
            if len(find) == 1:
                print("""There is no package name %s.\n"""
                      """I will use %s instead.""" %
                      (pkg_name, find[0]))
                pkg_name = find[0]
            else:
                print("""There is no package name %s,\n"""
                      """but the package names below include it.\n """
                      % pkg_name, "\n ".join(find))
                return (None, None)
        ix = self.vs["name"].index(pkg_name)
        if self.is_directed():
            pred = self.vs[self.predecessors(ix)]["name"]
            succ = self.vs[self.successors(ix)]["name"]
        else:
            pred = self.vs[self.neighbors(ix)]["name"]
            succ = None

        return (pred, succ)

    def normalize(self):
        "It recovers the values got bad during the GML write-read cycle."
        if "normalized" in dir(self) and self.normalized:
            return
        if "type" in self.vs.attributes():
            virtual = self.vs.select(type=1)
            for vertex in virtual:
                for attr in ("priority", "filesize",
                             "section", "summary", "version"):
                    vertex[attr] = None
                if "architecture" in self.vs.attributes():
                    vertex["architecture"] = None
        if "revision" in self.attributes():
            revision = self["revision"]
            if isinstance(revision, float) and not math.isnan(revision):
                self["revision"] = int(revision)

        del self.vs["id"]
        integer_attributes = (
            ("type", self.vs),
            ("filesize", self.vs),
            ("type", self.es),
        )
        for attr, object_ in integer_attributes:
            if attr in object_.attributes():
                for item in object_:
                    value = item[attr]
                    if isinstance(value, float) and\
                            not math.isinf(value) and not math.isnan(value):
                        item[attr] = int(value)
                    elif value is not None and (math.isinf(value) or math.isnan(value)):
                        print("The value of the {0} attribute is {1} ({2})."
                              .format(attr, value, item["name"]))
        self.normalized = True

    def cxcolorize(self, vcolors=("yellow", "lightblue"),
                   ecolors=("orange", "red", "blue")):
        "Colorize the packages according to the type (real or virtual)."
        for i in range(2):
            assert isinstance(vcolors[i], str),\
                "The vcolors parameter should contain two color names as string"
        for i in range(3):
            assert isinstance(ecolors[i], str),\
                "The ecolors parameter should contain three color names as string"
        self.normalize()
        if "type" in self.vs.attributes():
            for vertex in self.vs:
                vertex["color"] = vcolors[vertex["type"]]
        if "type" in self.es.attributes():
            for edge in self.es:
                edge["color"] = ecolors[edge["type"]]

    def cxneighborhood(self, pkg_name, plot=True, curvature=1, **kwargs):
        """Returns with the successors and predecessors and the package itself and can plot them.

        Parameters:
            pkg_name: string or integer
                The name of the package or the index of the vertex.
            plot: boolean or string, default False
                - If it is one  of "pdf", "png", "svg" or "ps", the output will
                  be a file like neighbors_of_pkg_name.pdf. With igraph 0.6.1+
                  you can use "eps" as well.
                - If other string, the output will be a file named in the string.
                - If True, plot to the screen.
                - If False, do not plot.
            **kwargs: dict
                keywords to the plot command

        Returns:
            Vertex sequence of the neighborhood.

        Example::

            >>> import cxnet
            >>> cxnet.load_netdata('ubuntu-10.10')
            'netdata/ubuntu-10.10-packages-2011-05-01.gml' have been loaded.
            >>> net.cxfind('vim')
            ['jvim-canna', 'libtext-vimcolor-perl', 'vim', 'vim-addon-manager', 'vim-common', 'vim-dbg', 'vim-gnome', 'vim-gtk', 'vim-gui-common', 'vim-latexsuite', 'vim-nox', 'vim-rails', 'vim-runtime', 'vim-tiny', 'vim-vimoutliner']
            >>> net.cxneighborhood("vim")
            <igraph.VertexSeq object at ...>
            >>> net.cxneighborhood("vim", plot=False)
            <igraph.VertexSeq object at ...>
        """

        if isinstance(pkg_name, int):
            ix = pkg_name
        else:
            assert isinstance(pkg_name, str),\
                "pkg_name must be string or integer"
            if pkg_name not in self.vs["name"]:
                find = self.cxfind(pkg_name)
                if len(find) == 1:
                    print("""There is no package name %s."""
                          """\nI will use %s instead.""" %
                          (pkg_name, find[0]))
                    pkg_name = find[0]
                elif len(find) > 1:
                    print("""There is no package name %s,"""
                          """\nbut the package names below include it.\n """ %
                          pkg_name,
                          "\n ".join(find))
                    return []
                else:
                    print("""There is no package name %s"""
                          """\nnor package name including it.""" % pkg_name)
                    return []
            ix = self.vs["name"].index(pkg_name)
        s = self.successors(ix)
        # TODO should have a more elaborated method:
        p = list(set(self.predecessors(ix)) - set(s))
        neighborhood = [ix]
        neighborhood.extend(p)
        neighborhood.extend(s)
        vs = self.vs(neighborhood)
        # TODO Should return with a subgraph, not with VertexSeq?

        if plot:
            attributes = self.vs.attributes()
            if "color" not in attributes and "type" in attributes:
                self.cxcolorize()
            shift = lambda y: 1 + curvature*math.cos(math.pi * y)
            coords = [(0, 0)]
            if p:
                delta = 1 / (len(p) - .99)
                y = -0.5
                for i in range(len(p)):
                    coords.append((-shift(y), y))
                    y += delta
            if s:
                delta = 1/(len(s)-.99)
                y = -0.5
                for i in range(len(s)):
                    coords.append((shift(y), y))
                    y += delta
            vs["coord"] = coords
            subnetwork = vs.subgraph()
            return_network = kwargs.pop("return_network", False)
            if kwargs.get("vertex_size") is None:
                kwargs["vertex_size"] = max(500/max(len(p), len(s), 5), 8)
            if kwargs.get("margin") is None:
                kwargs["margin"] = (70, max(0.6*kwargs["vertex_size"], 5)) * 2
            if kwargs.get("edge_arrow_width") is None:
                kwargs["edge_arrow_width"] = .5
            if plot in "pdf png svg ps eps".split():
                filename = "neighbors_of_%s.%s" % (pkg_name, plot)
                subnetwork.plot(filename, layout=subnetwork.vs["coord"],
                                **kwargs)
            elif isinstance(plot, str):
                subnetwork.plot(plot, layout=subnetwork.vs["coord"], **kwargs)
            else:
                subnetwork.plot(layout=subnetwork.vs["coord"], **kwargs)

        return self.subgraph(vs) if return_network else vs

    def cxdegdist(self, **kwargs):
        """Returns with a DegreDistribution class analyzing and plotting distribution.

        Parameter:
            kwargs:
                parameters to the DegreeDistribution class
                Eg. mode {"in", "out", None}

        Returns:
            dd: DegreeDistribution class object (see help(dd) )
        """
        return DegreeDistribution(self, **kwargs)

    def cxfind(self, namepart, verbosity=None):
        """Returns the ordered list of package names containing the given part.

        Parameter:
            namepart: string
                A part of the package name. At least 2 characters.

        Returns:
            names: ordered list of strings
                The ordered list of package names containing namepart.
        """
        assert len(namepart) > 1,\
            "the part of the name must contains at least 2 characters"
        names = [name for name in self.vs["name"] if namepart in name]
        names.sort()

        if verbosity:
            if "pkginfo" not in dir(self):
                self.pkginfo = PkgInfo()
            self.pkginfo.pkginfo(names, verbosity)
        return names

    def cxwrite(self, linux_distribution=linux_distribution,
                formats=["gml.zip", "graphmlz"]):
        """Writes the package dependency network into gml format.

        It writes a txt and a gml file into the current directory.
        The txt file contains some additional information about the
        deb-network, eg. the repositories used.

        Parameters:
            linux_distribution: 3-tuple or None
                (distribution name, dist. version with numbers, dist. version name)

        Returns:
            The name of the written files without extension.

        """

        if isinstance(formats, str):
            formats = formats.split()
        arch_time = gmtime()
        update_time = get_update_time()

        if isinstance(linux_distribution, tuple):
            d1, d2, d3 = linux_distribution
        elif linux_distribution is None:
            d1, d2, d3 = ["unknown"] * 3
            print("""I can not get the distribution name from the platform modul.
            Platform modul is too old.""")
        else:
            d1, d2, d3 = linux_distribution()
        distribution = " ".join([d1, d2, d3])
        self["distribution"] = distribution

        str_time = strftime("%Y-%m-%d_%H.%MGMT",
                            update_time if update_time else arch_time)
        name0 = "-".join([d1.lower(), d2, "packages", str_time])
        if not os.path.exists('netdata_zip'):
            os.mkdir('netdata_zip')
        if "gml.zip" in formats:
            print("Writing to compressed gml...")
            name = "{0}.gml".format(name0)
            self.write(name, format="gml")
            import zipfile
            filename = os.path.join('netdata_zip', '{0}.gml.zip'.format(name0))
            archive = zipfile.ZipFile(
                filename, 'w',
                compression=zipfile.ZIP_DEFLATED)
            archive.write(name)
            archive.close()
            os.remove(name)
            print("See file '{name}'.".format(name=filename))
        if "graphmlz" in formats:
            print("Writing to compressed GraphML (graphmlz)...")
            filename = "netdata_zip/%s.graphmlz" % name0
            self.write(filename, format="graphmlz")
            print("See file '{name}'.".format(name=filename))
        if "pickle" in formats:
            print("Writing to compressed pickle (Python specific)...")
            filename = "netdata_zip/%s.pickle" % name0
            self.write(filename)
            print("See file '{name}'.".format(name=filename))
        return name0

    def cxdescription(self, print_it=True):
        """Prints or returns the info attribute of the network.

        Parameter:
            print_it: boolean
                if it is True prints it, else returns with it.

        """
        info = self["Description"] if "Description" in self.attributes() else ""
        if print_it:
            print(info)
        else:
            return info

    # TODO handle multigraph (and diacriticals (ö) and unicode if it is possible)
    def to_networkx(self):
        """It convert the network into a Graph or Digraph of networkx.

        The result can be plotted with the matplotlib library.
        """
        if "label" in self.vs.attributes():
            names = self.vs["label"]
        elif "name" in self.vs.attributes():
            names = self.vs["name"]
        else:
            names = range(self.vcount())
        try:
            import networkx
        except ImportError:
            print("There is no module named networkx.\n"
                 "Install it if you want to convert igraph.Graph into networkx.(Di)Graph.")
            return
        if self.is_directed():
            net = networkx.DiGraph()
        else:
            net = networkx.Graph()
        edges = [(names[edge.source], names[edge.target]) for edge in self.es]
        net.add_edges_from(edges)
        return net

    def plot_with_networkx(self, layout=None, **kwargs):
        """Plots the network with networkx.

        It needs to have the matplotlib module installed.
        """
        net = self.to_networkx()
        import networkx
        draw_functions = {
            "circular": networkx.draw_circular,
            None: networkx.draw_spring,
            "spring": networkx.draw_spring,
            "shell": networkx.draw_shell,
            "spectral": networkx.draw_spectral,
            "random": networkx.draw_random,
        }
        draw = draw_functions[layout]
        draw(net, **kwargs)
        return net

    def cxsimplify(self, vertex=[], edge=[], test=False):
        """Remove the types of vertices and edges given in the
        arguments."""
        # TODO handle older networks without edge/vertex types
        # there were versions with vertex types but no edge types.
        for edge_attribute in edge:
            code = TYPES["edge"].get(edge_attribute)
            if code is not None:
                es = self.es.select(type=code)
                self.delete_edges(es)
                if test:
                    print("\t {0} {1} deleted".format(len(es), edge_attribute))
            else:
                raise TypeError("edge attribute", edge_attribute)  # TODO
        for vertex_attribute in vertex:
            code = TYPES["vertex"].get(vertex_attribute)
            if code is not None:
                vs = self.vs.select(type=code)
                self.delete_vertices(vs)
                if test:
                    print("\t {0} {1} deleted".format(len(vs),
                                                      vertex_attribute))
            elif vertex_attribute == "isolated":
                isolated_vertices = [
                    c[0] for c in self.clusters(igraph.WEAK)
                    if len(c) == 1
                    ]
                if test:
                    print("\t {0} {1} deleted".format(
                        len(isolated_vertices), vertex_attribute))
                self.delete_vertices(isolated_vertices)
            elif vertex_attribute in ["i386", "amd64"]:
                vs = self.vs.select(architecture=vertex_attribute)
                if test:
                    print("\t{0} vertex deleted (architecture {1})".format(
                        len(vs), vertex_attribute))
                self.delete_vertices(vs)
            else:
                raise TypeError("vertex attribute", vertex_attribute)  # TODO

    def cxstat_(self, attribute=None, object_="vertex"):
        "Prints the number of vertices/edges with the existing types."
        if attribute is None:
            attribute = "type"
        if object_ == "vertex":
            object_ = self.vs
        elif object_ == "edge":
            object_ = self.es
        else:
            raise TypeError("object_ must be None, 'vertex' or 'edge'")
        statdict = dict(
            (type_,
             len(eval("object_.select({0}=type_)".format(attribute),
                      dict(object_=object_, type_=type_)))
             )
            for type_ in set(object_[attribute]))
        for key in statdict:
            print("{1:6} {0}".format(key, statdict[key]))
        return statdict

    def vstat(self, attribute=None):
        return self.cxstat_(attribute)

    def estat(self, attribute=None):
        return self.cxstat_(attribute, object_="edge")

    @direction
    def cxclustering_degree_plot(self, min_degree=2, with_powerlaw=-1,
                                 **kwargs):
        """Plots the clustering coefficient as a function of degree.

        Parameters:
            min_degree: integer >= 2
                the minimal degree to take account
            with_powerlaw: int, float or None
                if integer or float, it plots a power-law function with this
                exponent, if None, it does not plot.
            mode: "in", "out" ,"" or None or cxnet.IN, cxnet.OUT, cxnet.ALL
                if "in" or "out", it uses indegree and outdegree instead of degree
                respectively
            coeff: int, float
                the coeff parameter of powerlaw.plot
            powerlaw_marker:
                marker of the power-law function
            powerlaw_linestyle:
                linestyle of the power-law function

        """
        direction = kwargs.pop("mode")
        powerlaw_parameters = dict(
            (param, kwargs.pop(param))
            for param
            in ["coeff", "powerlaw_marker", "powerlaw_linestyle"]
            if param in kwargs
        )
        degree = {
            igraph.IN: self.indegree,
            igraph.OUT: self.outdegree,
            igraph.ALL: self.degree,
        }[direction]
        assert isinstance(min_degree, int), "min_degree must be integer"
        assert min_degree >= 2, "min_degree must be 2 or greater"
        x, y = average_values(degree(), self.transitivity_local_undirected())
        new_kwargs = {"marker": "o", "linestyle": ""}
        new_kwargs.update(kwargs)
        kwargs = new_kwargs
        plot = pylab.loglog(x, y, label="average clustering coeff.", **kwargs)
        prefix = {igraph.IN: "in-", igraph.OUT: "out-"}.get(direction, "")
        pylab.title("Clustering coefficient as a function of {0}degree"
                    .format(prefix))
        pylab.xlabel("{0}degree".format(prefix))
        pylab.ylabel("average clustering coefficient")
        if with_powerlaw is not None:
            assert isinstance(with_powerlaw, (int, float)),\
                "with_powerlaw must be int, float or None"
            kwargs["marker"] = powerlaw_parameters.pop("powerlaw_marker", "")
            kwargs["linestyle"] = powerlaw_parameters.pop("powerlaw_linestyle",
                                                          "--")
            kwargs.update(powerlaw_parameters)
            powerlaw_plot(
                exponent=with_powerlaw,
                xmax=max(self.degree()),
                **kwargs
            )
        return plot


def debnetwork():
    """Creates the network of deb packages in Linux distributions using deb packages.

    Returns:
        A :class:`cxnet.Network` instance.

    It needs the `python-apt <http://apt.alioth.debian.org/python-apt-doc/>`_ package installed.
    """
    cdn = CommonDebNetwork()
    print("Transforming to numbered graph.")
    idgen = igraph.UniqueIdGenerator()  # igraph/datatypes.py
    edgelist = [(idgen[x], idgen[y]) for x, y, t in cdn.edges]
    [idgen[vertex] for vertex in cdn.vertices]
    package_names = idgen.values()
    print("Transforming to igraph.")
    debnet = Network(len(package_names), edgelist, directed=True)
    debnet.normalized = True
    debnet.es["type"] = [_type for _, _, _type in cdn.edges]
    debnet.sources_list = cdn.sources_list
    debnet.vs["name"] = idgen.values()
    for package_name in cdn.vertices:
        package_data = cdn.vertices[package_name]
        if package_data:
            vertex = debnet.vs[idgen[package_name]]
            (vertex["priority"],
             vertex["filesize"],
             vertex["section"],
             vertex["summary"],
             vertex["version"],
             vertex["architecture"],
             ) = package_data
    print("Setting vertex types.")
    debnet.vs["type"] = 0
    for extra in cdn.extra_vertices():
        debnet.vs[idgen[extra]]["type"] = 1
    debnet.type = "igraph"
    debnet["name"] = "software package dependency network of Linux"
    if cdn.revision:
        debnet["revision"] = cdn.revision
    debnet["hostname"] = platform.node()
    debnet["URL"] = "http://django.arek.uni-obuda.hu/cxnet"
    debnet["sources_list"] = cdn.sources_list
    debnet["architecture"], debnet["foreign_architectures"] = \
        ['\n'.join(archs) for archs in get_architectures()]
    debnet["Description"] = "Dependency network of Linux software packages"
    debnet["package_format"] = "deb"
    debnet["update_time"] = strftime("%Y-%m-%d %H:%M:%S GMT", get_update_time())
    debnet["Author"] = "Arpad Horvath"
    debnet["Creator"] = "cxnet"
    return debnet


def get_architectures():
    """Get the architecture and foreign architectures."""
    architectures = []
    for opt in ["print-architecture", "print-foreign-architectures"]:
        command = "dpkg --{0}".format(opt)
        stdout = os.popen(command)
        archs = [line.strip() for line in stdout.readlines() if line.strip()]
        architectures.append(archs)
    return architectures


def get_update_time():
    """Get the time of last update (last apt-get update)"""
    try:
        update_time = gmtime(os.path.getmtime("/var/lib/apt/lists/partial"))
    except OSError:
        update_time = None
    return update_time


def load_netdata(filename):
    """Loads netdata from a gml file in netdata directory.

    If it is not there, it will download it.

    Parameter:
        filename: string
            The name of the file we want to load (without extension)
            or the start of the filename. It loads the first file that
            match.

    Returns:
        A Network object with the archived network in it.

    Example::

        >>> import cxnet
        I have found an rc file: /home/ha/.cxnetrc.py.
        The graph_module was set in the rc file to "igraph".
        I will use igraph. (It have been imported.)
        >>> net=cxnet.load_netdata("as-")
        'netdata/as-22july06.gml' have been loaded.
        >>> print(net.summary())
        IGRAPH U--- 22963 48436 -- as-22july06.gml
        + attr: info (g), name (g), id (v), label (v)
        >>> print(net['info'])
        The file as-22july06.gml contains a symmetrized snapshot of the structure
        of the Internet at the level of autonomous systems, reconstructed from BGP
        tables posted at archive.routeviews.org.  This snapshot was created by Mark
        Newman from data for July 22, 2006 and is not previously published.
    """
    from archives import get_filepath
    head, tail = os.path.split(filename)
    if head or tail.endswith(".gml") or tail.endswith(".graphmlz"):
        os.path.isfile(filename)
        filepath = filename
    else:
        filepath = get_filepath(filename)
    if filepath:
        assert filepath.endswith(".gml") or filepath.endswith(".graphmlz")
        net = Network.Read(filepath)
        net.normalize()
        net["file"] = filename
        if "Description" not in net.attributes():
            infofile = open(os.path.splitext(filepath)[0] + ".txt")
            net["Description"] = "".join(infofile.readlines())
        if ("name" not in net.vs.attributes() and
                 "label" in net.vs.attributes()):
            net.vs["name"] = net.vs["label"]
        print("'{0}' have been loaded.".format(filepath))
        return net
    else:
        print("I can the file '{0}' neither find nor download.".format(filename))


def indegree_list(*networks):
    """Returns with the indegree list for all the packages in the networks.

    Parameters:
        *networks: The networks to be compared.

    Returns:
        with a dictionary. Its keys are the package names, and the values are the
        indegrees in the order of the given networks.

    """
    # TODO use for instead of reduce
    pkg_names = reduce(operator.or_, (set(net.vs["name"]) for net in networks))
    indegree_list = dict((pkg_name, []) for pkg_name in pkg_names)
    for network in networks:
        indegrees = dict(zip(network.vs["name"], network.indegree()))
        for pkg_name in pkg_names:
            indegree_list[pkg_name].append(indegrees.get(pkg_name))
    return indegree_list


def delta_k(network1, network2):
    """"""
    indegree_list_ = indegree_list(network1, network2)
    pairs = []
    for pkg_name in indegree_list_:
        old, new = indegree_list_[pkg_name]
        if None not in (old, new):
            pairs.append((old, new - old))
    return pairs
