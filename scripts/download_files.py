#!/usr/bin/env python
# coding: utf-8

"""Downloads the deb software package networks.

It compares the files in the actual directory with the
ones in the files.txt on the server and downloads the
ones are not here.
With the argument -l just lists the files to download.
"""

#TODO --url option to overwrite baseurl
# and automatic listing of the files in an Apache dir.
# https://github.com/mobileProgrammer/Automatic-Downloader

from __future__ import division
from __future__ import print_function
import sys
import os
import urllib

__author__ = 'Arpad Horvath'

baseurl = "http://django.arek.uni-obuda.hu/pack/"
file_list = "files.txt"

urllib.urlretrieve("".join([baseurl, file_list]),
                    os.path.join(".", file_list))
with open(file_list) as f:
    files = [line.strip() for line in f.readlines()]

files = set(files)
files_here = set(os.listdir('.'))
files_download = files - files_here


print("{0} files will be downloaded, {1} files is already here.".format
        (len(files_download), len(files_here)))

if len(sys.argv) > 1 and sys.argv[1] == "-l":
    print("New files\n- "+"\n- ".join(files_download))
    sys.exit()

for file_ in files_download:
    print("  ", file_)
    urllib.urlretrieve("".join([baseurl, file_]),
                    os.path.join(".", file_))

