# This script is intended to be sourced. It will set up a virtualenv
# if one doesn't already exist, and leave you ready to run the scripts
# in this folder.

HERE=$(dirname $(realpath ${BASH_SOURCE}))

if ! [[ -e ${HERE}/venv ]]; then
    python3 -m venv ${HERE}/venv
    source ${HERE}/venv/bin/activate
    pip install --upgrade pip
    pip install -e ${HERE}/..
else
    source ${HERE}/venv/bin/activate
fi

