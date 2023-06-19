#!/bin/python3
import argparse
import os
import sys

import operations.utils

import operations.install
import operations.remove
import operations.update
import operations.setenv
import operations.tools


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
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s" + str(operations.utils.Consts.version()),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        dest="verbose",
        default=False,
        help="Print more information",
    )

    subparser_manager = parser.add_subparsers(help="operation to perform", dest="operation")

    # add the operation commands
    operations.install.init_subparser(subparser_manager)
    operations.remove.init_subparser(subparser_manager)
    operations.update.init_subparser(subparser_manager)
    operations.setenv.init_subparser(subparser_manager)
    operations.tools.init_subparsers(subparser_manager)

    args = vars(parser.parse_args())

    # print the arguments for debugging
    if args["verbose"]:
        print(args)

    if operations.utils.check_dependencies() is False:
        sys.exit(1)
    else:
        if args["verbose"]:
            print("Dependencies are installed.")

    has_config = False
    current_config = operations.utils.LinuxMsvcConfig()
    try:
        current_config = operations.utils.LinuxMsvcConfig.load()
        has_config = True
        if args["verbose"]:
            print("Config file exists.")
            print(current_config)
    except FileNotFoundError:
        if args["verbose"]:
            print("No config file exists yet.")

    match args["operation"]:
        case "install":
            if has_config:
                print("A config file already exists.")
                print("If you want to reinstall linux-msvc, please uninstall it first.")
                print("To update use the update command.")
                sys.exit(1)

            current_config = operations.install.install(args)

        case "remove":
            if not has_config:
                if not args["destination"]:
                    print("No config file exists and no destination was given.")
                    print("Please specify a destination.")
                    sys.exit(1)

                current_config["destination"] = args["destination"]

            operations.remove.remove(current_config, args)

        case "meson":
            operations.tools.meson(current_config, args)
        case "wine":
            operations.tools.wine(current_config, args)

        case "setenv":
            operations.setenv.set_env(current_config, args)
