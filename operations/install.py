import os
import sys
import git
import operations.utils
import subprocess

from typing import Dict
from pathlib import Path

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


# A function to add the install command to the subparser
# This also sets up all the arguments for the install command
def init_subparser(subparser):
    install_parser = subparser.add_parser("install", help="Install linux-msvc")

    install_parser.add_argument(
        "--destination",
        default="~/msvc_linux",
        help="Where to install linux-msvc",
    )

    install_parser.add_argument(
        "--wine_prefix",
        default="~/msvc_linux/.winepref",
        help="Where to install the wine prefix",
    )

    install_parser.add_argument(
        "--msvc_path",
        default="~/msvc_linux/msvc",
        help="Where to install MSVC",
    )

    install_parser.add_argument(
        "--no_config_file",
        action="store_false",
        dest="create_config_file",
        default=True,
        help="Don't create a config file. The config file saves the paths and versions.",
    )

    install_parser.add_argument(
        "--no_cross_files",
        action="store_false",
        dest="copy_cross_files",
        default=True,
        help="Don't create cross files. The cross files are used by meson to cross compile.",
    )

    install_parser.add_argument(
        "--no_cache",
        action="store_false",
        dest="use_cache",
        default=True,
        help="Don't use the cache. This will cause the script to download everything again.",
    )


def install(args: Dict) -> operations.utils.LinuxMsvcConfig:
    config = operations.utils.LinuxMsvcConfig()
    config["destination"] = args["destination"]
    config["wine_prefix"] = args["wine_prefix"]
    config["msvc_path"] = args["msvc_path"]
    config["create_config_file"] = args["create_config_file"]
    config["copy_cross_files"] = args["copy_cross_files"]
    config["use_cache"] = args["use_cache"]

    if args["verbose"]:
        print(config)

    # Create the destination directory if it doesn't exist
    dest = Path(os.path.expanduser(config["destination"]))
    if not dest.exists():
        dest.mkdir(parents=True)

    msvc_path = Path(os.path.expanduser(config["msvc_path"]))
    if not msvc_path.exists():
        msvc_path.mkdir(parents=True)

    wine_prefix = Path(os.path.expanduser(config["wine_prefix"]))
    if not wine_prefix.exists():
        wine_prefix.mkdir(parents=True)

    cache_path = dest / "cache"
    if not cache_path.exists():
        cache_path.mkdir(parents=True)

    git.Repo.clone_from(
        "https://github.com/noah1510/linux-msvc",
        dest/"main-repo",
        verbose=args["verbose"],
    )

    git.Repo.clone_from(
        "https://github.com/mstorsjo/msvc-wine/",
        dest / "msvc-wine-repo",
        verbose=args["verbose"],
    )

    os.environ["WINEPREFIX"] = str(wine_prefix)
    os.environ["WINEARCH"] = "win64"

    dlcomand = [
        "python",
        str(dest / "msvc-wine-repo" / "vsdownload.py"),
        "--dest",
        str(msvc_path),
        "--accept-license"
    ]
    if config["use_cache"]:
        dlcomand.append("--cache")
        dlcomand.append(str(cache_path))

    if args["verbose"]:
        print("downloading msvc")
        print(dlcomand)
    subprocess.run(dlcomand)

    subprocess.run([
        str(dest / "msvc-wine-repo" / "install.sh"),
        str(msvc_path)
    ])

    if args["verbose"]:
        print("killing the wineserver")
    subprocess.run(["wineserver", "-k"])

    if args["verbose"]:
        print("making the wineserver persistent")
    subprocess.run(["wineserver", "-p"])

    if args["verbose"]:
        print("booting the wine server again")
    subprocess.run(["wine", "wineboot"])

    if args["verbose"]:
        print("change windows version to win10")
    subprocess.run(["winetricks", "settings", "win10"])

    if config["create_config_file"]:
        if args["verbose"]:
            print("saving the configuration")
        config.save()

    print("finished installing, to use you have to setup the environment variables.")
    print("Check the setenv operation for more information.")

    return config
