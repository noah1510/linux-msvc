import shutil
import sys
from typing import Dict

import semver
import os
import json


class Consts:
    @staticmethod
    def version() -> semver.VersionInfo:
        return semver.VersionInfo.parse("0.1.0")

    @staticmethod
    def get_configs_dir() -> os.path:
        if os.name != "posix":
            raise Exception("This function is only supported on posix systems.")

        if os.getenv("XDG_CONFIG_HOME") is not None:
            return os.getenv("XDG_CONFIG_HOME")

        if sys.platform == "darwin":
            return os.path.expanduser("~/Library/Preferences")

        return os.path.expanduser("~/.config")

    @staticmethod
    def get_app_config_dir(app_name: str) -> os.path:
        if os.name != "posix":
            raise Exception("This function is only supported on posix systems.")

        return os.path.join(Consts.get_configs_dir(), app_name)

    @staticmethod
    def config_file() -> os.path:
        return os.path.join(Consts.get_app_config_dir("msvc_linux"), "config.json")


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

    def save(self):
        with open(Consts.config_file(), "w") as f:
            json.dump(self, f, indent=4)

    @staticmethod
    def load() -> "LinuxMsvcConfig":
        if not os.path.exists(Consts.config_file()):
            raise FileNotFoundError(f"Config file {Consts.config_file()} does not exist.")

        with open(Consts.config_file(), "r") as f:
            return LinuxMsvcConfig(json.load(f))


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

