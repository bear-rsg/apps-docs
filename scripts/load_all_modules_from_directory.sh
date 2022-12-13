#!/bin/bash
set -e

DIR=$1

for app in $(cd ${DIR} ; ls); do
    for ver in $(cd ${DIR}/${app}; ls); do
        mod=$(realpath ${DIR}/${app}/${ver})
        ./add_module_info.py ${mod}
    done
done
