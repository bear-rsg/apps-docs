#!/bin/bash

HERE=`dirname $(realpath $0)`
cd ${HERE}

source activate.sh
./add_module_info.py $@

