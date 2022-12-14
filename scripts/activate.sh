# This script is intended to be sourced. It will leave you
# ready to run the scripts in this folder.

HERE=$(dirname $(realpath ${BASH_SOURCE}))

if ! [[ -e ${HERE}/venv ]]; then
    echo "Please set up a virtual environment (${HERE}/venv) and install this package and required db dependency."
else
    source ${HERE}/venv/bin/activate
fi

