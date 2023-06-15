import sys

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


def init_subparser(subparser):
    config_parser = subparser.add_parser("config", help="Configure linux-msvc")

    config_parser.add_argument(
        "--destination",
        default="",
        help="change the install location",
    )
