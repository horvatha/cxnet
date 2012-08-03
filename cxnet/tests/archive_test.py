"""Unittest for cxnet gml import."""

import cxnet
import os
import shutil
import unittest
import urllib2


def internet_on():
    try:
        response = urllib2.urlopen('http://google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        pass
    return False


class DebNetwork(unittest.TestCase):
    net = cxnet.debnetwork()
    print net.summary()

    def testCreateDebNetwork(self):
        self.assertTrue(isinstance(self.net, cxnet.Network))
        self.assertGreater(self.net.vcount(), 1000)
        self.assertGreater(self.net.ecount(), 1000)

    def testWriteDebNetwork(self):
        name0 = self.net.cxwrite()
        listdir = os.listdir(".")
        names = ["{0}.{1}".format(name0, ext) for ext in ("gml", "txt")]
        names.append(os.path.join('netdata_zip', '{0}.zip'.format(name0)))
        for name in names:
            self.assertTrue(os.path.isfile(name))
            self.assertGreater(os.stat(name).st_size, 0)


class NetData(unittest.TestCase):

    def testGetNetData(self):
        dirs = ("netdata", "netdata_zip")
        for dir_ in dirs:
            shutil.rmtree(dir_)
        cxnet.get_netdata("newman")
        for dir_ in dirs:
            self.assertTrue(os.path.isdir(dir_))
        self.assertEqual(len(os.listdir("netdata")),
                         2 * len(os.listdir("netdata_zip")))


class GML_files(unittest.TestCase):
    if not "netdata" in os.listdir("."):
        cxnet.get_netdata("newman")

    def testGMLOpen(self):
        net = cxnet.Network.Read("netdata/karate.gml")
        self.assertEqual(net.vcount(), 34)


if __name__ == "__main__":
    if internet_on():
        unittest.main()
    else:
        print("Internet it not on. I can not do the tests.")
