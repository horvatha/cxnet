#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
It pull (and will put) network data from (and to) archives.
"""

import urllib
import zipfile
import os
from .system import get_rc_dir

baseurls = (
    "http://www.arek.uni-obuda.hu/cxnet/deb_network/",
    "http://www-personal.umich.edu/~mejn/netdata/",
)

"""
The first item of the values is an url list or an url.
The second item of the values is the list of file names without zip extension,
or None. If it is None it downloads first the file_list.txt
and gets the file names from it.
"""
network_archives = {
    "newman": (baseurls[1:],
               """karate lesmis adjnoun football
               dolphins polblogs polbooks celegansneural
               power cond-mat cond-mat-2003 cond-mat-2005
               astro-ph hep-th netscience as-22july06""".split()
               ),
    "deb": (
        baseurls[:1],
        """
        ubuntu-12.04-packages-2012-04-26
        ubuntu-11.04-packages-2012-05-14
        ubuntu-11.10-packages-2012-04-25
        ubuntu-11.04-packages-2012-04-25
        ubuntu-11.04-packages-2011-09-20
        ubuntu-11.04-packages-2011-09-19
        ubuntu-10.10-packages-2011-05-01
        ubuntu-10.04-packages-2012-05-14
        ubuntu-10.04-packages-2010-10-25
        ubuntu-10.04-packages-2010-09-17
        ubuntu-10.04-packages-2010-08-19
        ubuntu-9.10-packages-2010-07-22
        ubuntu-9.10-packages-2010-07-16
        ubuntu-8.04-packages-2011-01-28
        debian-6.0-packages-2011-12-07
        debian-6.0-packages-2011-11-16
        debian-6.0-packages-2011-02-03
        """.split()
    ),
    "olddeb": (
        baseurls[:1],
        """
        ubuntu-9.04-packages-2009-11-03
        ubuntu-7.10-packages-2008-08-29
        """.split()
    ),
}


def get_archive_name(filename):
    """Returns with the archive name the archive file is in.

    Parameter:
        filename: string
            The name of the file we want to search without extension
            or the start of the filename. If it found one match it does not
            continue to search.

    Returns:
        A tuple: (archive_name, filename) if filename was found,
        else (None, None).

    Example::

        >>> import cxnet
        I have found an rc file: /home/ha/.cxnetrc.py.
        The graph_module was set in the rc file to "igraph".
        I will use igraph. (It have been imported.)
        >>> archive_name = cxnet.get_archive_name("lesmis")
        >>> archive_name
        ('newman', 'lesmis')
        >>> archive_name = cxnet.get_archive_name("les")
        lesmis
        >>> archive_name
        ('newman', 'lesmis')
        >>> archive_name = cxnet.get_archive_name("ub")
        ubuntu-10.04-packages-2010-08-19
        >>> archive_name
        ('deb', 'ubuntu-10.04-packages-2010-08-19')
    """
    file_list = []
    for archive in network_archives.keys():
        if filename in network_archives[archive][1]:
            file_list.append((archive, filename))
    for archive in network_archives.keys():
        for fn in network_archives[archive][1]:
            if fn.startswith(filename):
                file_list.append((archive, fn))
    return file_list


def get_filepath(filename):
    """Returns with the relative path of the file. If it is not here download it.

    Parameter:
        filename: string
            The name of the file we want to get (without extension)
            or the start of the filename. If it found one match it does not
            continue to search.

    Returns:
        The full relative path of the file or None if file was not found.
    """
    netdata_directory = get_netdata_directory()
    actual_dir = os.path.abspath(".")
    os.chdir(netdata_directory)
    if os.path.isdir('netdata'):
        files = os.listdir('netdata')
        files = [f for f in files if f.lower().endswith(".gml")]
        for fn in files:
            if fn == filename+'.gml':
                os.chdir(actual_dir)
                return os.path.join(netdata_directory, 'netdata', fn)
        for fn in files:
            if fn.startswith(filename):
                os.chdir(actual_dir)
                return os.path.join(netdata_directory, 'netdata', fn)
    archive_names = get_archive_name(filename)
    if archive_names:
        print("I will download datafiles.")
        get_netdata(archive_names[0])
    return os.path.join(netdata_directory, 'netdata', '{0}.gml'.format(fn))


def get_netdata(archive_name=None, unzip=True, path=get_rc_dir()):
    """Get network data from archives.

    It stores it in the netdata subdirectory of the current directory.
    The downloaded zipped files are in the netdata_zip subdirectory of the
    current directory.

    Parameter:
        archive_name: ``'newman'`` or ``'deb'``
           If ``newman``, it downloads a lot of network form
           Mark Newman's site.

           If ``deb``, it downloads a lot of deb package dependency
           network created with cxnet.

        unzip: boolean
           If True, it will unzip the archive files.

    Example::

        >>> import cxnet
        I have found an rc file: /home/ha/.cxnetrc.py.
        The graph_module was set in the rc file to "igraph".
        I will use igraph. (It have been imported.)
        >>> cxnet.get_netdata('deb')
        ubuntu-10.04-packages-2010-08-19.zip
            ubuntu-10.04-packages-2010-08-19.gml, ubuntu-10.04-packages-2010-08-19.txt
        ubuntu-10.04-packages-2010-10-25.zip
            ubuntu-10.04-packages-2010-10-25.gml, ubuntu-10.04-packages-2010-10-25.txt
        ubuntu-9.10-packages-2010-07-16.zip
            ubuntu-9.10-packages-2010-07-16.gml, ubuntu-9.10-packages-2010-07-16.txt
        ubuntu-9.10-packages-2010-07-22.zip
            ubuntu-9.10-packages-2010-07-22.gml, ubuntu-9.10-packages-2010-07-22.txt
        debian-6.0-packages-2011-02-03.zip
            debian-6.0-packages-2011-02-03.gml, debian-6.0-packages-2011-02-03.txt
    """

    if archive_name is None or archive_name not in network_archives.keys():
        print("""You need to choose an archive name.
Use one of them:""")
        for i in network_archives.keys():
            print("get_netdata(\"%s\")" % i)
        return

    actual_dir = os.path.abspath(".")
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    try:
        os.mkdir("netdata_zip")
    except OSError:
        pass  # directories exists
    try:
        os.mkdir("netdata")
    except OSError:
        pass  # directories exists

    baseurls, networks = network_archives[archive_name]
    for net in networks:
        zipfile_name = "%s.zip" % net
        baseurl = baseurls[0]
        url = "%s%s" % (baseurl, zipfile_name)
        stored_zipfile = os.path.join("netdata_zip", zipfile_name)
        urllib.urlretrieve(url, stored_zipfile)
        print(zipfile_name, end=": ")
        if unzip:
            try:
                zf = zipfile.ZipFile(stored_zipfile)
            except zipfile.BadZipfile as e:
                print(e.message)
            else:
                print(", ".join(zf.namelist()))
                # zf.extractall("netdata") # Not in older versions (2.5).
                for name in zf.namelist():
                    bites = zf.read(name)
                    f = open(os.path.join("netdata", name), "w")
                    f.write(bites)
                    f.close()
    os.chdir(actual_dir)


def put_debnetdata():
    """Put the data of debian package dependency network into the archive.
    """
    print("""Send them to Arpad Horvath <horvath.arpad@arek.uni-obuda.hu>.""")


def get_netdata_directory():
    """Try to find the netdata directory.

    If is can not find. It returns with a default.
    On posix systems, like Linux, Unix and MacOSX:
        ~/.cxnet/netdata
    On nt systems, like Windows XP, Windows 7, Windows Vista:
        ~/_cxnet/netdata

    """
    for parent_dir in (
            os.path.expanduser("~/.cxnet"),
            os.path.expanduser("~/_cxnet"),
            ".",
            "..",
            "../cxnet",
            os.path.expanduser("~"),
    ):
        if os.path.isdir(parent_dir):
            netdata_dir = os.path.join(parent_dir, "netdata")
            if os.path.isdir(netdata_dir):
                return parent_dir

    return get_rc_dir() or "."

if __name__ == "__main__":
    for archive in network_archives.keys():
        get_netdata(archive)
