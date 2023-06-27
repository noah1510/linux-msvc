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
        "--delete_main_repo",
        action="store_true",
        default=False,
        help="Don't delete the main repo. This will keep the main repo.",
    )

    remove_parser.add_argument(
        "--keep_vcpkg",
        action="store_true",
        default=False,
        help="Don't delete the vcpkg installation. This will keep the vcpkg installation.",
    )


class RemoveDirectory(Dict):
    def __init__(
            self,
            path: Path,
            verbose: bool,
            condition: bool = True,
            directory_name: str = None,
    ):
        super().__init__()
        self["path"] = path
        self["verbose"] = verbose
        self["condition"] = condition
        if directory_name is None:
            self["directory_name"] = path.name
        else:
            self["directory_name"] = directory_name

    def remove(self):
        if not self["condition"]:
            return

        if self["path"].exists():
            if self["verbose"]:
                print(f"Removing {self['directory_name']} directory: {self['path']}")
            shutil.rmtree(self["path"])


def remove(conf: operations.utils.LinuxMsvcConfig, uninstall_conf: Dict):
    dirs_to_remove = [
        RemoveDirectory(
            conf.destination() / "cache",
            verbose=uninstall_conf["verbose"],
            condition=uninstall_conf["delete_cache"],
            directory_name="cache",
        ),
        RemoveDirectory(
            conf.destination() / ".wineenv",
            verbose=uninstall_conf["verbose"],
            condition=not uninstall_conf["keep_wine_prefix"],
            directory_name="wine prefix",
        ),
        RemoveDirectory(
            conf.destination() / "msvc",
            verbose=uninstall_conf["verbose"],
            condition=not uninstall_conf["keep_msvc"],
            directory_name="msvc_install",
        ),
        RemoveDirectory(
            conf.destination() / "msvc-wine-repo",
            verbose=uninstall_conf["verbose"],
            condition=not uninstall_conf["keep_msvc"],
            directory_name="msvc_wine_repo",
        ),
        RemoveDirectory(
            conf.destination() / "vcpkg",
            verbose=uninstall_conf["verbose"],
            condition=not uninstall_conf["keep_vcpkg"],
            directory_name="vcpkg",
        ),
        RemoveDirectory(
            conf.destination() / "main-repo",
            verbose=uninstall_conf["verbose"],
            condition=uninstall_conf["delete_main_repo"],
            directory_name="main_repo",
        ),
        RemoveDirectory(
            operations.utils.Consts.config_file().parent,
            verbose=uninstall_conf["verbose"],
            condition=True,
            directory_name="config folder",
        ),
    ]

    for directory in dirs_to_remove:
        directory.remove()
