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
import signal

__author__ = 'Arpad Horvath'

finish = False
def signal_handler(signal, frame):
    global finish
    finish = True

def download_files(baseurl, file_list, extra_files):
    urllib.urlretrieve(os.path.join(baseurl, file_list),
                        os.path.join(".", file_list))
    with open(file_list) as f:
        files = [line.strip() for line in f.readlines()]

    files = set(files)
    files_here = set(os.listdir('.'))
    common_files = files_here & files
    files_download = sorted(list(files - files_here))

    print("{0} files will be downloaded, {1} files is here, {2} files is here from the file list.".format
            (len(files_download), len(files_here), len(common_files)))

    if len(sys.argv) > 1 and sys.argv[1] == "-l":
        print("New files\n- "+"\n- ".join(files_download))
        sys.exit()

    for file_set in [files_download, set(extra_files)]:
        for file_ in file_set:
            print("  ", file_)
            urllib.urlretrieve("".join([baseurl, file_]),
                            os.path.join(".", file_))
            if finish:
                sys.exit(1)

for baseurl, file_list in [
        ("http://django.arek.uni-obuda.hu/pack/ubuntu1204_on_debian/", "files.txt"),
        ("http://ns.arek.uni-obuda.hu/repo/pack/ubuntu1204_on_debian/", "files_ns.txt"),
        ]:
    extra_files = ["number_of_nodes_and_edges"]
    signal.signal(signal.SIGINT, signal_handler)
    download_files(baseurl, file_list, extra_files)

