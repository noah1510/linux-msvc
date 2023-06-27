import sys
import git

import operations.utils
import operations.tools
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
        "--no_wine_prefix",
        dest="no_wine_prefix",
        action="store_true",
        default=False,
        help="don't override the wine prefix with dest/.wineenv",
    )

    install_parser.add_argument(
        "--no_config_file",
        action="store_false",
        dest="create_config_file",
        default=True,
        help="Don't create a config file. The config file saves the paths and versions.",
    )

    install_parser.add_argument(
        "--no_cache",
        action="store_false",
        dest="use_cache",
        default=True,
        help="Don't use the cache. This will cause the script to download everything again.",
    )

    install_parser.add_argument(
        "--use_system_winetricks",
        action="store_true",
        default=False,
        dest="system_winetricks",
        help="Use the system winetricks instead of the downloaded one.",
    )


def install(args: Dict) -> operations.utils.LinuxMsvcConfig:
    config = operations.utils.LinuxMsvcConfig()
    config["destination"] = args["destination"]
    config["no_wine_prefix"] = args["no_wine_prefix"]
    config["create_config_file"] = args["create_config_file"]
    config["use_cache"] = args["use_cache"]
    config["system_winetricks"] = args["system_winetricks"]

    if args["verbose"]:
        print(config)

    # Create the destination directory if it doesn't exist
    if not config.destination().exists():
        config.destination().mkdir(parents=True)

    # download and install msvc
    setup_msvc(config, args["verbose"])

    # create the wine prefix and install all winetricks
    setup_wine(config, args["verbose"])

    # download and install the powershell
    setup_powershell(config, args["verbose"])

    # setup vcpkg (broken atm because no vs install is found)
    setup_vcpkg(config, args["verbose"])

    # download and setup chocolatey
    setup_choco(config, args["verbose"])

    # save the config file
    if config["create_config_file"]:
        if args["verbose"]:
            print("saving the configuration")
        config.save()

    print("finished installing.")
    print("use 'linux-msvc shell' to start a shell with the environment set up.")
    print("Or use the 'linux-msvc meson command to run meson with the environment set up.")

    return config


def setup_msvc(config: operations.utils.LinuxMsvcConfig, verbose=False):
    operations.utils.set_env(config, {}, verbose)

    msvc_path = Path(config.destination() / "msvc")
    if not msvc_path.exists():
        msvc_path.mkdir(parents=True)

    cache_path = config.destination() / "cache"
    if not cache_path.exists():
        cache_path.mkdir(parents=True)

    if not (config.destination() / "msvc-wine-repo").exists():
        git.Repo.clone_from(
            "https://github.com/mstorsjo/msvc-wine/",
            config.destination() / "msvc-wine-repo",
            verbose=verbose,
        )

    # download and setup msvc-wine
    dlcomand = [
        "python",
        str(config.destination() / "msvc-wine-repo" / "vsdownload.py"),
        "--dest",
        str(msvc_path),
        "--accept-license"
    ]
    if config["use_cache"]:
        dlcomand.append("--cache")
        dlcomand.append(str(cache_path))

    if verbose:
        print("downloading msvc")
        print(dlcomand)
    subprocess.run(dlcomand)

    subprocess.run([
        str(config.destination() / "msvc-wine-repo" / "install.sh"),
        str(msvc_path)
    ])


def setup_wine(config: operations.utils.LinuxMsvcConfig, verbose=False):
    operations.utils.set_env(config, {}, verbose)

    if verbose:
        print("killing the wineserver")
    subprocess.run(["wineserver", "-k"])

    winetricks_packages = [
        ["settings", "win10"],
        ["7zip"],
        ["cmake"],
        ["dotnet48"],
        ["dotnet_verifier"],
        ["settings", "win10"],
        ["nuget"],

    ]
    operations.tools.install_winetricks_packages(config, winetricks_packages, verbose)

    if verbose:
        print("killing the wineserver")
    subprocess.run(["wineserver", "-k"])

    if verbose:
        print("making the wineserver persistent")
    subprocess.run(["wineserver", "-p"])

    if verbose:
        print("booting the wine server again")
    subprocess.run(["wine", "wineboot"])


def setup_powershell(config: operations.utils.LinuxMsvcConfig, verbose=False):
    operations.utils.set_env(config, {}, verbose)

    powershell_url = "https://github.com/PowerShell/PowerShell/releases/download/v7.3.4/PowerShell-7.3.4-win-x64.msi"
    powershell_installer = operations.utils.get_chached_file(config, powershell_url, verbose=verbose)

    subprocess.run([
        "wine",
        "msiexec.exe",
        "/quiet",
        "/i",
        str(powershell_installer)
    ])


def setup_vcpkg(config: operations.utils.LinuxMsvcConfig, verbose=False):
    operations.utils.set_env(config, {}, verbose)

    if not (config.destination() / "vcpkg").exists():
        git.Repo.clone_from(
            "https://github.com/microsoft/vcpkg",
            config.destination() / "vcpkg",
            verbose=verbose,
        )

    vcpkg_setup_args = [
        "-File",
        str(config.destination() / "scripts" / "bootstrap.ps1"),
        "-disableMetrics",
    ]

    operations.tools.powershell(config, {"verbose": verbose, "args": vcpkg_setup_args})


def setup_choco(config: operations.utils.LinuxMsvcConfig, verbose=False):
    operations.utils.set_env(config, {}, verbose)

    download_url = "https://community.chocolatey.org/install.ps1"
    download_path = operations.utils.get_chached_file(config, download_url, verbose=verbose)

    choco_setup_args = [
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(download_path),
    ]

    operations.tools.powershell(config, {"verbose": verbose, "args": choco_setup_args})
