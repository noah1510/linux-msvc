import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

import operations.utils

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


def init_subparser(subparser):
    shell_parser = subparser.add_parser("shell", help="Start a shell with the environment set up")

    shell_parser.add_argument(
        "--type",
        default="",
        help="The type of shell to start. The default is the current shell.",
    )


def set_env(config: operations.utils.LinuxMsvcConfig, args: Dict):

    dest = Path(config["destination"]).expanduser()
    os.environ['PATH'] = str(dest / "msvc" / "bin" / "x64") + ':' + os.environ['PATH']

    if not config["no_wine_prefix"]:
        wine_prefix = Path(dest / ".wineenv")
        os.environ["WINEPREFIX"] = str(wine_prefix)

    os.environ["WINEARCH"] = "win64"

    env_command = [
        "env",
        "msvcenv.sh",
    ]

    subprocess.run(env_command)
