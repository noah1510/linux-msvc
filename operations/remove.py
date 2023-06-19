import os
import shutil
import sys
import operations.utils

from typing import Dict
from pathlib import Path

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


# A function to add the remove command to the subparser
# This also sets up all the arguments for the remove command
def init_subparser(subparser):
    remove_parser = subparser.add_parser("remove", help="remove/uninstall linux-msvc")

    remove_parser.add_argument(
        "--destination",
        default="~/msvc_linux",
        help="Where to install linux-msvc. This is used when no config file is present.",
    )

    remove_parser.add_argument(
        "--delete_cache",
        action="store_true",
        default=False,
        help="Delete the cache. This will cause the script to download everything again for the next install.",
    )

    remove_parser.add_argument(
        "--keep_wine_prefix",
        action="store_true",
        default=False,
        help="Don't delete the wine prefix. This will keep the wine prefix and all setup configs in it.",
    )

    remove_parser.add_argument(
        "--keep_msvc",
        action="store_true",
        default=False,
        help="Don't delete the msvc installation. This will keep the msvc installation and the msvc wine repo.",
    )

    remove_parser.add_argument(
        "--keep_cross_files",
        action="store_true",
        default=False,
        help="Don't delete the cross files.",
    )


def remove_dir(
    directory: Path,
    verbose: bool,
    dirname: str,
):
    if directory.exists():
        if verbose:
            print(f"Removing {dirname} directory: {directory}")
        shutil.rmtree(directory)


def remove(conf: operations.utils.LinuxMsvcConfig, uninstall_conf: Dict):
    dest_dir = Path(os.path.expanduser(conf["destination"]))

    if uninstall_conf["delete_cache"]:
        cache_dir = dest_dir / "cache"
        remove_dir(cache_dir, uninstall_conf["verbose"], "cache")

    if not uninstall_conf["keep_wine_prefix"]:
        prefix_dir = dest_dir / ".wineenv"
        remove_dir(prefix_dir, uninstall_conf["verbose"], "wine prefix")

    if not uninstall_conf["keep_msvc"]:
        msvc_dir = dest_dir / "msvc"
        msvc_wine_dir = dest_dir / "msvc_wine"

        remove_dir(msvc_dir, uninstall_conf["verbose"], "msvc_install")
        remove_dir(msvc_wine_dir, uninstall_conf["verbose"], "msvc_wine_repo")

    if not uninstall_conf["keep_cross_files"]:
        cross_files_dir = dest_dir / "cross_files"
        remove_dir(cross_files_dir, uninstall_conf["verbose"], "cross_files")

    remove_dir(dest_dir/"main-repo", uninstall_conf["verbose"], "linux-msvc")
    config_folder = operations.utils.Consts.config_file().parent
    remove_dir(config_folder, uninstall_conf["verbose"], "config folder")