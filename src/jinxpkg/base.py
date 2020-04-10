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
    jinxpkg_location = ''
    if sys.version[0] == str(2):
        import pkgutil
        jinxpkg_location = pkgutil.get_loader('jinxpkg').filename
    elif sys.version[0] == str(3):
        import importlib
        jinxpkg_location = os.path.join(importlib.util.find_spec("jinxpkg").origin, os.pardir)
    template_path = os.path.abspath(os.path.join(jinxpkg_location, "template", "init"))
    template_file = open(template_path, "r")
    package_name = os.path.basename(pkg_dir)
    inf = template_file.read().replace("{{package_name}}", "'{}'".format(package_name))
    init_file.write(inf)
    template_file.close()
    init_file.close()


def make_version_file(module_dir, version):
    version_file = open(os.path.join(module_dir, "VERSION"), "w+")
    version_file.write(str(version))
    version_file.close()
    return
