import subprocess
import sys
import argparse
from pathlib import Path

import operations.utils
import operations.setenv

from typing import Dict

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


def init_subparsers(subparser):
    meson_parser = subparser.add_parser("meson", help="A wrapper around meson to use it with msvc")
    wine_parser = subparser.add_parser("wine", help="Use msvc wine")

    meson_parser.add_argument(
        "--add_cross_file",
        dest="add_cross_file",
        action="store_true",
        default=False,
        help="Add the cross file to the meson command",
    )

    meson_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to meson",
    )

    wine_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to wine",
    )


def meson(
    config: operations.utils.LinuxMsvcConfig,
    args: Dict
):
    operations.setenv.set_env(config, args)

    meson_command = ["meson"]
    meson_command += args["args"]

    subprocess.run(["bash", "-c", "'echo $PATH'"])

    cross_file_dest = Path(config["destination"]) / "main-repo" / "cross_files" / "wine_msvc"
    if args["add_cross_file"]:
        meson_command += [
            "--cross-file",
            str(cross_file_dest)
        ]

    subprocess.run(meson_command)


def wine(
    config: operations.utils.LinuxMsvcConfig,
    args: Dict
):
    wine_command = [
        "env",
        config["destination"] + "/msvc/bin/x64/msvcenv.sh",
        config["destination"] + "/msvc/bin/x64/wine-msvc.sh",
        args["args"]
    ]

    subprocess.run(wine_command)
