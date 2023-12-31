import sys

# don't allow running the file as script
if __name__ == "__main__":
    print("This file is not meant to be run as script.")
    sys.exit(1)


# A function to add the update command to the subparser
# This also sets up all the arguments for the update command
def init_subparser(subparser):
    update_parser = subparser.add_parser("update", help="Update linux-msvc")

    update_parser.add_argument(
        "--destination",
        default="~/msvc_linux",
        help="Where to install linux-msvc",
    )

