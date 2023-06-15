import sys

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
