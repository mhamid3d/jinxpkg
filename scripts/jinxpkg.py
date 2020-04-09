import argparse
import logging
import os
import re
import sys
import subprocess
import json
import shutil

ARGPARSER = None
ARGS = None
PROG = "jinxpkg"
DEFAULT_GIT = "https://github.com/mhamid3d/{}.git"
DEFAULT_PUBLISH = os.path.abspath("C:/tools")

LOGGER = logging.getLogger("jinxpkg")
LOGGER.setLevel(logging.DEBUG)
logging.basicConfig()


def init_opt():
    global ARGPARSER

    ARGPARSER = argparse.ArgumentParser(
        description="Pipeline Package Management & Information",
        prog=PROG,
        formatter_class=argparse.HelpFormatter
    )
    ARGPARSER.add_argument(
        "action", action="store", metavar="", help="action to run"
    )
    ARGPARSER.add_argument(
        "-p",
        "--package",
        dest="package",
        type=str,
        required=True,
        help="""
        Directory to clone the git repo to. The package will live here
             """
    )
    # ARGPARSER.add_argument(
    #     "-ng",
    #     "--no-git",
    #     dest="nogit",
    #     action="store_true",
    #     help="Skip cloning the git repository, if it is already cloned and given as an arguement in --create"
    # )
    ARGPARSER.add_argument(
        "-g",
        "--git",
        dest="git",
        type=str,
        help="git repo name. If this is left empty it will search for the repo by the package name via -p"
    )
    ARGPARSER.add_argument(
        "-d",
        "--directory",
        dest="directory",
        default=DEFAULT_PUBLISH,
        type=str,
        help="Publish directory. If not given it will fallback to the default: {}".format(DEFAULT_PUBLISH)
    )
    ARGPARSER.add_argument(
        "-t",
        "--type",
        dest="type",
        default="JINX",
        type=str,
        help="""
        The subtype directory for the published tool. Default to JINX for global tools.
        If you need to publish your tool to a show, this is where you enter the showname.
        Alternativly you can enter USER, and it will publish the tool to the users directory
             """
    )


def validate_publish(args):
    package_name = args.package
    local_path = os.path.abspath(args.package)
    publish_type = args.type
    publish_dir = os.path.join(args.directory, args.type)
    script_dir = os.path.join(local_path, "scripts")

    try:

        # ----- ASSERT LOCAL PACKAGE PATH EXISTS ----- #
        assert os.path.exists(local_path), "Package Dir Could Not Be Found At...{}".format(str(local_path))

        LOGGER.info("##### Package Path..........OK")

        # ----- ASSERT CONFIG FILE ----- #
        config_file = os.path.join(local_path, "CONFIG")
        assert os.path.exists(config_file), "Config File Could Not Be Found At...{}".format(str(config_file))
        with open(config_file, "r") as cf:
            data = json.load(cf)
            cf.close()

        required_keys = ["package", "version", "context"]
        for key in required_keys:
            assert key in data.keys(), "Required key '{}' missing from CONFIG File".format(key)
            assert data[key], "Required key '{}' returns None in CONFIG File".format(key)
            if key == "version":
                target_dir = os.path.join(
                    publish_dir, data['context'],
                    data['package'],
                    "{}-{}".format(data['package'], data['version'])
                )
                assert not os.path.exists(
                    target_dir
                ), "Package '{}' With Version '{}' Of Target '{}' Already Exists! Edit the Config version.".format(
                    data['package'], data['version'], args.type)

        assert str(data['package']) == str(args.package), "Given Package Name Doesn't Match With CONFIG Package Name!"

        LOGGER.info("##### Config File...........OK")

        # ----- ASSERT SOURCE FILES EXISTS ----- #
        source_dir = os.path.join(local_path, "src", data['package'])
        assert os.path.exists(source_dir), "Source Dir Could Not Be Found At...{}".format(str(source_dir))

        LOGGER.info("##### Source Files..........OK")

        return package_name, source_dir, script_dir, publish_dir, data['version'], data['context']

    except AssertionError as ae:

        LOGGER.error(ae.args[0])

        return False


def main():
    init_opt()
    global ARGS

    ARGS = ARGPARSER.parse_args()

    if ARGS.action == "create":
        package_name = ARGS.package
        git_name = ARGS.git
        git_addr = DEFAULT_GIT.format(git_name) if git_name else DEFAULT_GIT.format(package_name)
        pkg_dir = os.path.abspath(package_name)

        LOGGER.info("Fetching repository from Git Address: {}".format(git_addr))
        LOGGER.info("Target directory: {}".format(pkg_dir))

        subprocess.call(["git", "clone", git_addr, pkg_dir])

        LOGGER.info("Making template directories...")

        os.mkdir(os.path.join(pkg_dir, "src"))
        os.mkdir(os.path.join(pkg_dir, "src", package_name))
        src_init = open(os.path.join(pkg_dir, "src", package_name, "__init__.py"), "w+")
        src_init.close()
        os.mkdir(os.path.join(pkg_dir, "tests"))
        os.mkdir(os.path.join(pkg_dir, "scripts"))

        LOGGER.info("Creating CONFIG file...")
        config_path = os.path.join(pkg_dir, "CONFIG")
        config_file = open(config_path, "w+")
        config_file.close()

        config_data = {
            "package": package_name,
            "version": "1_0_0",
        }
        LOGGER.info("Writing CONFIG data...")
        with open(config_path, "w+") as cf:
            json.dump(config_data, cf, indent=4, sort_keys=True, )
            cf.close()

    elif ARGS.action == "publish":
        is_valid = validate_publish(ARGS)
        if is_valid:
            package_name, source_dir, script_dir, publish_dir, version, source_ctx = is_valid
            target_source = os.path.join(publish_dir, source_ctx, package_name)
            if not os.path.exists(target_source):
                os.mkdir(target_source)
                #TODO: add this version to jinxpkg.json since this is the first publish
            module_dir = os.path.join(target_source, "{}-{}".format(package_name, version))
            shutil.copytree(source_dir, module_dir)
            if os.path.exists(script_dir) and os.listdir(script_dir):
                for script in os.listdir(script_dir):
                    script_file = os.path.join(script_dir, script)
                    script_name_agnostic = os.path.splitext(script)[0]
                    target_script_file = os.path.join(publish_dir, "scripts", script_name_agnostic)
                    shutil.copy(script_file, target_script_file)




if __name__ == '__main__':
    main()
    sys.exit(0)
