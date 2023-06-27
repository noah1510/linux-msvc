import sys

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
