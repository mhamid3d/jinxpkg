from __future__ import absolute_import

import sys
import os
import yaml


def getPackageRelease(init=None, package=None):
    jinxf_path = os.path.abspath(os.path.join(init, os.pardir, os.pardir, os.pardir, "jinx.pkg"))
    jinxf = open(jinxf_path, "r")
    jinx_data = yaml.safe_load(jinxf)
    release = "{}-{}".format(package, jinx_data[str(package)])
    return release
