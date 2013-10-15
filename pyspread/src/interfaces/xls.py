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

xls
===

This file contains interfaces to Excel xls file format.

"""

from datetime import datetime
from itertools import product

import xlrd

import src.lib.i18n as i18n

from src.lib.selection import Selection

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class Xls(object):
    """Interface between code_array and xls file

    The xls file is read from disk with the read method.
    The xls file is written to disk with the write method.

    Parameters
    ----------

    code_array: model.CodeArray object
    \tThe code_array object data structure
    workbook: xlrd Workbook object
    \tFile like object in xls format

    """

    def __init__(self, code_array, workbook):
        self.code_array = code_array
        self.workbook = workbook

    def _code2xls(self):
        """Writes code to xls file

        Format: <row>\t<col>\t<tab>\t<code>\n

        """

#        for key in self.code_array:
#            key_str = u"\t".join(repr(ele) for ele in key)
#            code_str = self.code_array(key)
#            out_str = key_str + u"\t" + code_str + u"\n"
#
#            self.pys_file.write(out_str.encode("utf-8"))

    def _xls2code(self, worksheet, tab):
        """Updates code in pys code_array"""

        type2mapper = {
            0: lambda x: None,  # Empty cell
            1: lambda x: repr(x),  # Text cell
            2: lambda x: repr(x),  # Number cell
            3: lambda x: repr(datetime(
                xlrd.xldate_as_tuple(x, self.workbook.datemode))),  # Date
            4: lambda x: repr(bool(x)),  # Boolean cell
            5: lambda x: repr(x),  # Error cell
            6: lambda x: None,  # Blank cell
        }

        rows, cols = worksheet.nrows, worksheet.ncols
        for row, col in product(xrange(rows), xrange(cols)):
            cell_type = worksheet.cell_type(row, col)
            cell_value = worksheet.cell_value(row, col)

            key = row, col, tab
            self.code_array[key] = type2mapper[cell_type](cell_value)

    # Access via model.py data
    # ------------------------

    def from_code_array(self):
        """Replaces everything in xls_file from code_array"""

    def to_code_array(self):
        """Replaces everything in code_array from xls_file"""

        worksheets = self.workbook.sheet_names()
        for tab, worksheet_name in enumerate(worksheets):
            worksheet = self.workbook.sheet_by_name(worksheet_name)
            self._xls2code(worksheet, tab)
