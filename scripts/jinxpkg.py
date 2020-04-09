import argparse
import logging
import os
import re
import sys
import subprocess
import json

ARGPARSER = None
ARGS = None
PROG = "jinxpkg"
DEFAULT_GIT = "https://github.com/mhamid3d/{}.git"

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
        os.mkdir(os.path.join(pkg_dir, "tests"))
        os.mkdir(os.path.join(pkg_dir, "scripts"))

        LOGGER.info("Creating CONFIG file...")
        config_path = os.path.join(pkg_dir, "CONFIG")
        config_file = open(config_path, "w+")

        config_data = {
            "package": package_name,
            "version": "1_0_0",
        }
        LOGGER.info("Writing CONFIG data...")
        with open(config_path, "w+") as cf:
            json.dump(config_data, cf, indent=4, sort_keys=True, )


if __name__ == '__main__':
    main()
    sys.exit(0)