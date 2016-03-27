#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

ods
===

This file contains interfaces to the OpenDocument Spreadsheet file format.

It is split into the following sections

 * shape
 * code
 * attributes
 * row_heights
 * col_widths
 * macros

"""

import src.lib.i18n as i18n

# Use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext

class Ods(object):
    """Interface between code_array and ods file

    The ods file is read from disk with the read method.
    The ods file is written to disk with the write method.

    Parameters
    ----------

    code_array: model.CodeArray object
    \tThe code_array object data structure
    ods_file: file
    \tFile like object in ods format

    """

    def __init__(self, code_array, pys_file):
        self.code_array = code_array
        self.pys_file = pys_file