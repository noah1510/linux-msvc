#!/bin/bash

# a function to get the fill path name of a given path
# $1: the path to get the full path name
# return: the full path name
function full_readlink() {
    # if the path starts with ~, replace it with $HOME and store it in a variable
    if [[ "$1" == ~* ]]; then
        path="$HOME${1:1}"
    else
        path="$1"
    fi

    # use the readlink command to get the full path name
    # if the readlink command is not available, use python to get the full path name
    if command -v readlink &> /dev/null; then
        path="$(readlink -f -- "$path")"
    else
        path="$(python -c "import os; print(os.path.realpath('$path'))")"
    fi

    echo "$path"
}

# get the directory the script is located in
file_dir="$( dirname -- "$( full_readlink "$0"; )";)"
echo "Script directory: $file_dir"

# get the configs directory
if [ "$XDG_CONFIG_HOME" = "" ]; then
    # use the default path for either darwin or linux
    if [ "$(uname)" == "Darwin" ]; then
        config_dir="$HOME/Library/Preferences"
    else
        config_dir="$HOME/.config"
    fi
else
    config_dir="$XDG_CONFIG_HOME"
fi

config_file="$config_dir/msvc_linux/config.json"
# check if the config file exists
no_config_file="$( [ ! -f "$config_file" ] && echo "true"; )"
if [ "$no_config_file" = "true" ]; then

    # run the first install script
    echo "Running first install script"

    # check if a custom destination is in the arguments
    install_location="$HOME/msvc_linux"
    for arg in "$@"; do
        # check for both --destination dest and --destination=*
        if [[ "$arg" == --destination ]]; then
            install_location="$2"
            install_location="$(full_readlink "$install_location"; )"
        elif [[ "$arg" == --destination* ]]; then
            install_location="${arg#*=}"
            install_location="${install_location#* }"
            install_location="$(full_readlink "$install_location"; )"
        fi
    done

    echo "Installing to $install_location"

    # create the install dir if it does not exist
    if [ ! -d "$install_location" ]; then
        mkdir -p "$install_location"
    fi

    # abort if git is not installed
    if ! command -v git &> /dev/null; then
        echo "Git is not installed. Please install git and try again."
        exit 1
    fi

    # clone the repository if it does not exist
    if [ ! -d "$install_location"/main-repo ]; then
        git clone https://github.com/noah1510/linux-msvc "$install_location"/main-repo
    fi

    # change into the repo directory
    cd "$install_location/main-repo" || exit 1

    pipenv install

    # execute the linux-msvc script from the repo
    pipenv run python3 "$install_location"/main-repo/linux-msvc.py install "$@"
    # check if the script was executed successfully
    if [ $? -ne 0 ]; then
        echo "The script exited with an error. Please check the output for more information."
        exit 1
    fi

    # put a wrapper_fle in $USER/.local/bin
    if [ ! -d "$HOME/.local/bin" ]; then
        mkdir -p "$HOME/.local/bin"
    fi

    SCRIPT_LOCATION="$HOME/.local/bin/linux-msvc"
    echo "#!/bin/bash" > "$SCRIPT_LOCATION"
    echo 'PARENT_COMMAND=$(ps -o comm= $PPID)' >> "$SCRIPT_LOCATION"
    echo "export PIPENV_PIPFILE=\"$install_location/main-repo/Pipfile\"" >> "$SCRIPT_LOCATION"
    echo "pipenv run python3 $install_location/main-repo/linux-msvc.py --base_shell \$PARENT_COMMAND \"\$@\"" >> "$SCRIPT_LOCATION"

    chmod +x "$HOME/.local/bin/linux-msvc"
    exit 0
fi

echo "Use this script only for the initial install"
echo "however the install command was not used or there is already an installation"
exit 1
