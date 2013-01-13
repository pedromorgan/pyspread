#!/bin/bash

# Makes pot file po/pyspread.pot from src

xgettext --language=Python --keyword=_ --output=po/pyspread.pot `find . -name "*.py"`
