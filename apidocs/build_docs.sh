#!/bin/bash


HERE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR=`realpath $HERE_DIR/..`
echo $ROOT_DIR

sphinx-build -a  -b html $ROOT_DIR/apidocs $ROOT_DIR/public/