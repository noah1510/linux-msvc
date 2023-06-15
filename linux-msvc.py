#!/bin/python3
import argparse
import os
import sys
import operations.install
import operations.uninstall
import operations.update
import operations.setenv

# make sure the os is not windows
if os.name == "nt":
    print("This script is not meant to be run on windows.")
    sys.exit(1)

# also block on java
if os.name == "java":
    print("This script is not meant to be run on java.")
    sys.exit(1)

# check if fish is used as shell
shell_type = ''
shell = os.path.realpath(f'/proc/{os.getppid()}/exe')
if shell.endswith("fish"):
    shell_type = "fish"
elif shell.endswith("bash"):
    shell_type = "bash"
    print("Bash is not officially supported yet.")
    print("Some features might not work as expected.")
elif shell.endswith("zsh"):
    shell_type = "zsh"
    print("Bash is not officially supported yet.")
    print("Some features might not work as expected.")
else:
    print("This script is only supported on fish, bash and zsh.")
    sys.exit(1)


# parse the command line arguments if run as script
if __name__ == "__main__":

    main_msg = "This projects allows using MSVC on linux.\n"
    main_msg += "At the moment only fish is supported.\n"
    main_msg += "Bash and zsh support will be added in the future."

    parser = argparse.ArgumentParser(description=main_msg)
    subparser_manager = parser.add_subparsers(help="operation to perform", dest="operation")

    # add the operation commands
    operations.install.init_subparser(subparser_manager)
    operations.uninstall.init_subparser(subparser_manager)
    operations.update.init_subparser(subparser_manager)
    operations.setenv.init_subparser(subparser_manager)

    args = vars(parser.parse_args())
    print(args)

    if operations.install.check_dependencies() is False:
        sys.exit(1)
    else:
        print("Dependencies are installed.")
