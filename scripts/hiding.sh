#!/bin/bash

HERE=`dirname $(realpath $0)`
cd ${HERE}

source activate.sh
./hiding.py $@

