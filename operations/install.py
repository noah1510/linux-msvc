import sys
import shutil

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
