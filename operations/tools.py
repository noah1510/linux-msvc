import subprocess
import sys
import argparse

import operations.utils

from typing import Dict

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


def init_subparsers(subparser):
    cl_parser = subparser.add_parser("cl", help="Use the cl compiler")
    link_parser = subparser.add_parser("link", help="Use the msvc linker")
    wine_parser = subparser.add_parser("wine", help="Use msvc wine")

    cl_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to cl",
    )

    link_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to link",
    )

    wine_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to wine",
    )


def cl(
    config: operations.utils.LinuxMsvcConfig,
    args: Dict
):
    cl_command = [
        "env",
        config["destination"] + "/msvc-wine-repo/wrappers/msvcenv.sh",
        config["destination"] + "/msvc-wine-repo/wrappers/cl",
        args["args"]
    ]

    subprocess.run(cl_command)


def link(
    config: operations.utils.LinuxMsvcConfig,
    args: Dict
):
    cl_command = [
        "env",
        config["destination"] + "/msvc-wine-repo/wrappers/msvcenv.sh",
        config["destination"] + "/msvc-wine-repo/wrappers/link",
        args["args"]
    ]

    subprocess.run(cl_command)


def wine(
    config: operations.utils.LinuxMsvcConfig,
    args: Dict
):
    wine_command = [
        "env",
        config["destination"] + "/msvc-wine-repo/wrappers/msvcenv.sh",
        config["destination"] + "/msvc-wine-repo/wrappers/wine-msvc.sh",
        args["args"]
    ]

    subprocess.run(wine_command)
