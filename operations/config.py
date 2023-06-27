import os
import sys
from pathlib import Path
from typing import Dict

import operations.utils
import operations.remove
import operations.install

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


def init_subparser(subparser):
    config_parser = subparser.add_parser("config", help="Configure linux-msvc")

    conf_operation_subparser = config_parser.add_subparsers(help="config operation to perform", dest="conf_operation")
    reset_parser = conf_operation_subparser.add_parser("reset", help="Reset a configuration")
    reset_parser.add_argument(
        "reset_module",
        help="The module to reset",
        choices=["all", "wine_prefix", "msvc"],
    )


def configure(config: operations.utils.LinuxMsvcConfig, args: Dict):
    match args["conf_operation"]:
        case "reset":
            reset(config, args)


def reset(config: operations.utils.LinuxMsvcConfig, args: Dict):
    match args["reset_module"]:
        case "all":
            reset_msvc(config, verbose=args["verbose"])
            reset_prefix(config, verbose=args["verbose"])
        case "wine_prefix":
            reset_prefix(config, verbose=args["verbose"])
        case "msvc":
            reset_msvc(config, verbose=args["verbose"])


def reset_prefix(config: operations.utils.LinuxMsvcConfig, verbose=False):
    if not config["no_wine_prefix"]:
        prefix_location = Path(config["destination"]).expanduser() / ".wineenv"
    else:
        if os.environ["WINEPREFIX"]:
            prefix_location = Path(os.environ["WINEPREFIX"])
        else:
            prefix_location = Path("~/.wine").expanduser()

    try:
        operations.remove.RemoveDirectory(prefix_location, verbose=verbose, directory_name="wine prefix").remove()
    except FileNotFoundError:
        pass

    operations.install.setup_wine(config, verbose=verbose)
    operations.install.setup_powershell(config, verbose=verbose)
    operations.install.setup_vcpkg(config, verbose=verbose)
    operations.install.setup_choco(config, verbose=verbose)


def reset_msvc(config: operations.utils.LinuxMsvcConfig, verbose=False):
    msvc_dir = config.destination() / "msvc"
    msvc_wine_dir = config.destination() / "msvc-wine-repo"

    try:
        operations.remove.RemoveDirectory(msvc_dir, verbose=verbose, directory_name="msvc_install").remove()
        operations.remove.RemoveDirectory(msvc_wine_dir, verbose=verbose, directory_name="msvc_wine_repo").remove()
    except FileNotFoundError:
        pass

    operations.install.setup_msvc(config, verbose=verbose)


