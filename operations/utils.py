import shutil
import subprocess
import sys
from typing import Dict
from pathlib import Path

import semver
import os
import json

import wget


class Consts:
    @staticmethod
    def version() -> semver.VersionInfo:
        return semver.VersionInfo.parse("0.1.0")

    @staticmethod
    def get_configs_dir() -> Path:
        if os.name != "posix":
            raise Exception("This function is only supported on posix systems.")

        if os.getenv("XDG_CONFIG_HOME") is not None:
            return Path(os.getenv("XDG_CONFIG_HOME"))

        if sys.platform == "darwin":
            return Path(os.path.expanduser("~/Library/Preferences"))

        return Path(os.path.expanduser("~/.config"))

    @staticmethod
    def get_app_config_dir(app_name: str) -> Path:
        if os.name != "posix":
            raise Exception("This function is only supported on posix systems.")

        return Consts.get_configs_dir() / app_name

    @staticmethod
    def config_file() -> Path:
        return Consts.get_app_config_dir("msvc_linux") / "config.json"


class LinuxMsvcConfig(Dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, key: str, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def set(self, key: str, value):
        self[key] = value

    def destination(self) -> Path:
        return Path(self.get("destination")).expanduser()

    def save(self):
        target_location = os.path.dirname(Consts.config_file())
        if not os.path.exists(target_location):
            os.makedirs(target_location, exist_ok=True)

        with open(Consts.config_file(), "w") as f:
            json.dump(self, f, indent=4)

    @staticmethod
    def load() -> "LinuxMsvcConfig":
        if not os.path.exists(Consts.config_file()):
            raise FileNotFoundError(f"Config file {Consts.config_file()} does not exist.")

        with open(Consts.config_file(), "r") as f:
            return LinuxMsvcConfig(json.load(f))


# returns the full path of a cached file
# if it doesn't exist, download it
# if no filename is given, the filename will be the basename of the download url
def get_chached_file(config: LinuxMsvcConfig, download_url: str, file_name: str = None, verbose=False) -> Path:
    cache_dir = config.destination() / "cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    if file_name is None:
        file_name = os.path.basename(download_url)

    cached_file = cache_dir / file_name
    if not os.path.exists(cached_file):
        if verbose:
            print(f"Downloading {file_name}...")
        wget.download(url=download_url, out=str(cached_file), bar=None)

    return cached_file


# check if the required dependencies are installed
# if not, print a message and return false
# if yes, return true
def check_dependencies() -> bool:
    dependencies = ["wine", "winetricks", "git", "msiextract", "winbindd"]
    for dep in dependencies:
        if shutil.which(dep) is None:
            print(f"Error: {dep} is not installed.")
            print("wine, winetricks, git, msitools and winbind are required. Install them and try again.")
            return False

    return True


def set_env(config: LinuxMsvcConfig, args: Dict, verbose=False):

    dest = Path(config["destination"]).expanduser()
    os.environ['PATH'] = str(dest / "msvc" / "bin" / "x64") + ':' + os.environ['PATH']

    if not config["no_wine_prefix"]:
        wine_prefix = Path(dest / ".wineenv")
        os.environ["WINEPREFIX"] = str(wine_prefix)

    os.environ["WINEARCH"] = "win64"

    if not verbose:
        if "verbose" in args:
            verbose = args["verbose"]

    if not verbose:
        os.environ["WINEDEBUG"] = "-all"

    env_command = [
        "env",
        "msvcenv.sh",
    ]

    subprocess.run(env_command)
