#!/bin/bash

HERE_DIR=`dirname "$BASH_SOURCE"`
ROOT_DIR=`realpath $HERE_DIR/..`
echo $ROOT_DIR

python3 $ROOT_DIR/docs/create_pyqt_objects.py pyqt5 --use-qt-uri
sphinx-build -n -v -a -b html $ROOT_DIR/docs $ROOT_DIR/public/