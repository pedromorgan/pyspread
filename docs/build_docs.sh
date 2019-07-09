#!/bin/bash

echo $BASH_SOURCE

HERE_DIR=`dirname "$BASH_SOURCE"`
ROOT_DIR=`realpath $HERE_DIR/..`
echo $ROOT_DIR

sphinx-build -n -v -a -b html $ROOT_DIR/docs $ROOT_DIR/public/