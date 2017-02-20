#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/mn/prog/Phoenix

# Calls pyspread from top level folder of extracted tarball
export PYTHONPATH=$PYTHONPATH:./pyspread
python3 ./pyspread/pyspread $@
