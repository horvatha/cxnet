#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creates the dependency network of the deb files of Linux distributions based on
Debian distribution like:
    - Debian itself
    - Ubuntu variants (Ubuntu, Kubuntu, Xubuntu...)

The generated network can be transform into IGraph or NetworkX Graph object.
"""

from __future__ import with_statement
#from __future__ import division
from __future__ import print_function
import sys
from apt import Cache
import apt_pkg
version_compare = apt_pkg.VersionCompare if "VersionCompare" in dir(apt_pkg) else apt_pkg.version_compare
if apt_pkg.version_compare(apt_pkg.VERSION, "0.7.23") < 0:
        print("Must use python-apt 0.7.23 or greater.")
        sys.exit(1)
from cxnet.revision import get_revision
import glob
import re

TYPES = dict(
    vertex = dict(
        real = 0,
        virtual=1,
    ),
    edge = dict(
        depends=0,
        recommends=1,
        provides=2,
        suggests=3, #Not yet stored.
        )
    )

note_about_dependencies = """
Packages can depend from not existing packages.

Three type of examples:

1.
twiki depends on apache | apache2 | apache2.2
| means one of the three is enough to satisfy the dependency
There is no apache package, but there is apache2,
so we can install twiki.

2.
python-psycopg2da depends on zope3
There is no zope3, so python-psycopg2da can not installed.

3.
xpaint depends on editor
editor is not a real package, but several packages can provide editor
such as vim, nano, emacs,
so xpaint can be installed.
This type of package is called virtual package.
"""

def sources_list():
    """Returns the sources from the /etc/apt/sources.list file.

    Just returns with the lines beginning with "deb "'.

    See: man sources.list
    """
    source_files = ["/etc/apt/sources.list"]
    source_files.extend(glob.glob("/etc/apt/sources.list.d/*.list"))
    deb_regexp = re.compile(r"\s*deb ")

    all_lines = []
    for source_file in source_files:
        with open(source_file) as f:
            lines = f.readlines()
            all_lines.extend([line for line in lines if deb_regexp.match(line)])

    return "".join(all_lines)

def get_deps(pkg):
    """Get the dependencies for a given apt.Package object.
    Works with the oldest and newest versions of apt_pkg.
    It does not work with version <=0.6.46.
    """
    deps = None
    try:
        "This works with python-apt versions >= 0.7.23"
        cand = pkg.candidate
    except AttributeError:
        "This works with python-apt versions <= 0.7.14"
        deps = pkg.candidateDependencies
    else:
        if cand:
            deps = cand.dependencies
    return deps

class CommonDebNetwork:
    """Common class to create igraph.Graph or networkx.Graph.
    Before conversion you should use self.purge_edges().
    """
    def __init__(self):
        self.create()
        self.has_purged_edges = False
    def __len__(self):
        return len(self.vertices)

    def create(self):
        """Creates the lists of package names and edges of the
        package dependency network from the apt cache.
        """

        print("""Getting package names and dependencies.""")
        cache=Cache()
        pkg_list = [pkg for pkg in cache]

        depends_edges = set()
        for pkg in pkg_list:
            pkgname = pkg.name
            depnames = set()
            cand = pkg.candidate
            if cand:
                deps = cand.dependencies
                recommends = cand.recommends
                for _type, relation in enumerate([deps, recommends]):
                    for dep in relation:
                        or_deps = dep.or_dependencies
                        for or_dep in or_deps:
                            dep_name = or_dep.name
                            depends_edges.add((pkgname, dep_name, _type))

        provided_edges = set()
        for pkg in pkg_list:
            _type = 2
            candidate = pkg.candidate
            if candidate:
                for virtual in candidate.provides:
                    provided_edges.add((virtual, pkg.name, _type))

        self.vertices = dict((pkg.name, self.package_tuple(pkg)) for pkg in cache)
        self.edges = edges = depends_edges | provided_edges
        self.sources_list = sources_list()
        self.revision = get_revision()

    def package_tuple(self, pkg):
        candidate = pkg.candidate
        if candidate:
            return (
                    candidate.priority,
                    candidate.size,
                    candidate.section,
                    candidate.summary.replace('"', "''"),
                    candidate.version,
                    candidate.architecture,
                   )
        else:
            return None

    def summary(self):
        # print "{0:5} vertices, {1:6} edges".format(len(self.vertices), len(self.edges))
        # Does work with 2.5 used in Debian Lenny.
        print("%5s vertices, %6s edges" % (len(self.vertices), len(self.edges)))

    def extra_targets(self):
        """Targets not in vertices."""
        extra = set(target for _, target, _ in self.edges if not target in self.vertices)
        return extra
    def extra_sources(self):
        """Sources not in vertices."""
        extra = set(source for source, _, _ in self.edges if not source in self.vertices)
        return extra

    def extra_vertices(self):
        """Sources and targets not in vertices."""
        return self.extra_sources() | self.extra_targets()

    def purge_edges(self):
        """Remove edges, which target is not in self.vertices."""
        print("""Removing edges, which target is not in self.vertices.""")
        extra_targets = self.extra_targets()
        new_edges = [edge for edge in self.edges if not edge[1] in extra_targets]
        self.edges = new_edges
        self.has_purged_edges = True

class PkgInfo:
    def __init__(self, verbosity=1):
        self.cache = Cache()
        self.verbosity = verbosity

    def pkginfo(self, pkgs, verbosity=None):
        self.set_verbosity(verbosity)
        if not self.verbosity:
            return
        if not isinstance(pkgs, (list,tuple)):
            pkgs = [pkgs]
        for pkg in pkgs:
            _pkg = "  %s  " % pkg
            print(_pkg.center(60, "-"))
            if pkg not in self.cache:
                print("No package named '%s'." % pkg)
                continue
            cache = self.cache[pkg]
            if self.verbosity == 1:
                print(cache.summary)
            elif self.verbosity > 1:
                print(cache.rawDescription)
            if self.verbosity > 2:
                versions = cache.versions
                if versions:
                    print("- Versions:")
                    for version in versions.keys():
                        print("  %s" % version)
            print()

    def set_verbosity(self, verbosity):
        if verbosity is None:
            return
        if verbosity in [0,1,2,3]:
            self.verbosity = verbosity

if __name__ == "__main__":
    print("apt_pkg version: {0}, date: {1}".format(apt_pkg.VERSION, apt_pkg.Date))
    network = CommonDebNetwork()
    network.summary()
