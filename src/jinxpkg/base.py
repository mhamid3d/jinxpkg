import os
import sys
import yaml


def version_exists(scope, package, version):
    return os.path.exists(os.path.join('/tools/{0}/python/{1}/{1}-{2}'.format(scope, package, version)))


def get_jinx_file(scope='JINX'):
    return os.path.abspath('/tools/{}/jinx.pkg'.format(scope))


def update_version(package=None, version=None, scope='JINX'):
    assert version_exists(scope, package, version), "{}-{} does not exist or is not published!".format(package, version)
    jinx_file = get_jinx_file(scope=scope)
    ojf = open(jinx_file, "r")
    data = yaml.safe_load(ojf)
    data = {} if not data else data
    ojf.close()
    data[str(package)] = str(version)
    ojf = open(jinx_file, "w")
    yaml.dump(data, ojf)
    ojf.close()
    return True


def make_package_init(pkg_dir):
    assert os.path.exists(pkg_dir), "Location Does Not Exist: {}".format(pkg_dir)
    init_file = open(os.path.join(pkg_dir, "__init__.py"), "w+")
    init_file.close()
