import subprocess
import sys
import argparse
from pathlib import Path

import operations.utils

from typing import Dict, List

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


def init_subparsers(subparser):
    meson_parser = subparser.add_parser("meson", help="A wrapper around meson to use it with msvc")
    wine_parser = subparser.add_parser("wine", help="Use msvc wine")
    powershell_parser = subparser.add_parser("pwsh", help="Use the powershell (pwsh.exe) inside wine")

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

    powershell_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to pwsh",
    )


def meson(
    config: operations.utils.LinuxMsvcConfig,
    args: Dict
):
    operations.utils.set_env(config, args)

    meson_command = ["meson"]
    meson_command += args["args"]

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
    operations.utils.set_env(config, args)

    wine_command = ["wine-msvc.sh"]
    wine_command += args["args"]
    subprocess.run(wine_command)


def powershell(
    config: operations.utils.LinuxMsvcConfig,
    args: Dict
):
    operations.utils.set_env(config, args)

    pwsh_command = ["wine"]
    pwsh_command += ["C:\\Program Files\\PowerShell\\7\\pwsh.exe"]
    pwsh_command += args["args"]
    if "verbose" in args and args["verbose"]:
        print(pwsh_command)

    subprocess.run(pwsh_command)


def install_winetricks_packages(
        config: operations.utils.LinuxMsvcConfig,
        packages: List[List[str]],
        verbose=False
):

    winetricks_exe = 'winetricks'
    if not config["system_winetricks"]:
        winetricks_exe_url = "https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks"
        winetricks_exe = operations.utils.get_chached_file(
            config,
            winetricks_exe_url,
            file_name="winetricks",
            verbose=verbose
        )

    operations.utils.set_env(config, {}, verbose)

    for package in packages:
        print("installing wintricks package: ", package)

        args = [str(winetricks_exe), "-q"]
        args.extend(package)

        subprocess.run(args)
