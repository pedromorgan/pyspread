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

pys
===

This file contains interfaces to the native pys file format.

It is split into the following sections

 * shape
 * code
 * attributes
 * row_heights
 * col_widths
 * macros

"""

import ast
from collections import OrderedDict
from itertools import imap

from src.lib.selection import Selection


class Pys(object):
    """Interface between data_array and pys file

    The pys file is read from disk with the read method.
    The pys file is written to disk with the write method.

    Parameters
    ----------

    data_array: model.DataArray object
    \tThe data_array object data structure
    pys_file: file
    \tFile like object in pys format

    """

    def __init__(self, data_array, pys_file):
        self.data_array = data_array
        self.pys_file = pys_file

        self._section2reader = {
            "Pyspread save file version": self._pys_assert_version,
            "shape": self._pys2shape,
            "code": self._pys2code,
            "attributes": self._pys2attributes,
            "row_heights": self._pys2row_heights,
            "col_widths": self._pys2col_widths,
            "macros": self._pys2macros,
        }

        self._section2writer = OrderedDict([
            ("Pyspread save file version", self._version2pys),
            ("shape", self._shape2pys),
            ("code", self._code2pys),
            ("attributes", self._attributes2pys),
            ("row_heights", self._row_heights2pys),
            ("col_widths", self._col_widths2pys),
            ("macros", self._macros2pys),
        ])

    def _split_tidy(self, string, maxsplit=None):
        """Rstrips string for \n and splits string for \t"""

        if maxsplit is None:
            return string.rstrip("\n").split("\t")
        else:
            return string.rstrip("\n").split("\t", maxsplit)

    def _get_key(self, *keystrings):
        """Returns int key tuple from key string list"""

        return tuple(imap(int, keystrings))

    def _pys_assert_version(self, line):
        """Asserts pys file version"""

        assert line == "0.1"

    def _version2pys(self):
        """Writes pys fiel version"""

    def _shape2pys(self):
        """Updates shape in pys file data"""

    def _pys2shape(self, line):
        """Updates shape in data_array"""

        self.data_array.shape = self._get_key(*self._split_tidy(line))

    def _code2pys(self):
        """Updates code in pys file data"""

    def _pys2code(self, line):
        """Updates code in pys data_array"""

        row, col, tab, code = self._split_tidy(line, maxsplit=3)
        key = self._get_key(row, col, tab)

        self.data_array[key] = unicode(code, encoding='utf-8')

    def _attributes2pys(self):
        """Updates attributes in pys file data"""

    def _pys2attributes(self, line):
        """Updates attributes in data_array"""

        splitline = self._split_tidy(line)

        selection_data = map(ast.literal_eval, splitline[:5])
        selection = Selection(*selection_data)

        tab = int(splitline[5])

        attrs = {}
        for col, ele in enumerate(splitline[6:]):
            if not (col % 2):
                # Odd entries are keys
                key = ast.literal_eval(ele)

            else:
                # Even cols are values
                attrs[key] = ast.literal_eval(ele)

        self.data_array.cell_attributes.append((selection, tab, attrs))

    def _row_heights2pys(self):
        """Updates row_heights in pys file data"""

    def _pys2row_heights(self, line):
        """Updates row_heights in data_array"""

        # Split with maxsplit 3
        row, tab, height = self._split_tidy(line)
        key = self._get_key(row, tab)

        try:
            self.data_array.row_heights[key] = float(height)

        except ValueError:
            pass

    def _col_widths2pys(self):
        """Updates col_widths in pys file data"""

    def _pys2col_widths(self, line):
        """Updates col_widths in data_array"""

        # Split with maxsplit 3
        col, tab, width = self._split_tidy(line)
        key = self._get_key(col, tab)

        try:
            self.data_array.col_widths[key] = float(width)

        except ValueError:
            pass

    def _macros2pys(self):
        """Updates macros in pys file data"""

        self.pys_file_data["macros"] = self.data_array.dict_grid.macros

    def _pys2macros(self, line):
        """Updates macros in data_array"""

        self.data_array.dict_grid.macros += "\n"
        self.data_array.dict_grid.macros += line

    # Access via model.py data
    # ------------------------

    def from_data_array(self):
        """Replaces everything in file_data from data_array"""

        for key in self._section2writer:
            self._section2writer[key]()

    def to_data_array(self):
        """Replaces everything in data_array from file_data"""

        state = None

        for line in self.pys_file:
            if line in self._section2reader:
                state = line

            elif state is not None:
                self._section2reader[state](line)
