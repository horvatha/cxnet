#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

if sys.version_info < (2, 6):
    print("This module requires Python >= 2.6")
    sys.exit(0)

description="""
The cxnet extends IGraph module with some functionality
I am using in higher education.
Some functionality is available with NetworkX module as well.
Function plotting needs matplotlib (pylab).

Functionalities:
- Creating networks with multifractal network generator.
- Creating network from the deb package hierarchy.
- Investigating and plotting degree distribution.
- Graph methods:

 * to list the vertices with most degrees,
 * to plot the neighbours of a vertex.

- A tool to create network evolution models.
"""

options = dict(
    name = 'cxnet',
    version = '0.3',
    description = 'Complex networks in education',
    long_description = description,
    license = 'BSD License',

    author = 'Arpad Horvath',
    author_email = 'horvath.arpad.szfvar@gmail.com',
    url = 'http://django.arek.uni-obuda.hu/cxnet/doc',

    #package_dir = {'igraph': 'igraph'},
    packages = ['cxnet' ], #, 'oldmfng', 'network_evolution'],
    #scripts = ['scripts/igraph'],
    #test_suite = "igraph.test.suite",

    platforms = 'ALL',
    keywords = ['graph', 'network', 'mathematics', 'math', 'graph theory', 'discrete mathematics', 'complex networks'],
    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Education',
      'Intended Audience :: Science/Research',
      'Intended Audience :: Information Technology',
      'Intended Audience :: System Administrators',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering',
      'Topic :: Scientific/Engineering :: Information Analysis',
      'Topic :: Scientific/Engineering :: Mathematics',
      'Topic :: Scientific/Engineering :: Physics',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'License :: OSI Approved :: BSD License',
    ]
)

setup(**options)
