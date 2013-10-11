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

        # pys_file_data is a dict of the pys file section strings
        # i.e. {"shape": "1000\t100\t3\n", ...}
        self.pys_file_data = {}

    def _split_tidy(self, string, maxsplit=None):
        """Rstrips string for \n and splits string for \t"""

        if maxsplit is None:
            return string.rstrip("\n").split("\t")
        else:
            return string.rstrip("\n").split("\t", maxsplit)

    def _get_key(self, *keystrings):
        """Returns int key tuple from key string list"""

        return tuple(imap(int, keystrings))

    def _shape2pys(self):
        """Updates shape in pys file data"""

    def _pys2shape(self):
        """Updates shape in data_array"""

        shape_code = self.pys_file_data["shape"]
        self.data_array.shape = self._get_key(*self._split_tidy(shape_code))

    def _code2pys(self):
        """Updates code in pys file data"""

    def _pys2code(self):
        """Updates code in pys data_array"""

        code_code = self.pys_file_data["code"]

        for line in code_code.split("\n"):
            row, col, tab, code = self._split_tidy(line, maxsplit=3)
            key = self._get_key(row, col, tab)

            self.data_array[key] = unicode(code, encoding='utf-8')

    def _attributes2pys(self):
        """Updates attributes in pys file data"""

    def _pys2attributes(self):
        """Updates attributes in data_array"""

        attributes_code = self.pys_file_data["attributes"]

        for line in attributes_code.split("\n"):
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

    def _pys2row_heights(self):
        """Updates row_heights in data_array"""

        row_heights_code = self.pys_file_data["row_heights"]

        for line in row_heights_code.split("\n"):
            # Split with maxsplit 3
            row, tab, height = self._split_tidy(line)
            key = self._get_key(row, tab)

            try:
                self.data_array.row_heights[key] = float(height)

            except ValueError:
                pass

    def _col_widths2pys(self):
        """Updates col_widths in pys file data"""

    def _pys2col_widths(self):
        """Updates col_widths in data_array"""

        col_widths_code = self.pys_file_data["col_widths"]

        for line in col_widths_code.split("\n"):
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

    def _pys2macros(self):
        """Updates macros in data_array"""

        self.data_array.dict_grid.macros = self.pys_file_data["macros"]

    # Access via pys file
    # -------------------

    def read(self):
        """Read pys file to pys file data"""

        raise NotImplementedError

    def write(self):
        """Write pys file to disk"""

        raise NotImplementedError

    def clear_file_data(self):
        """Removes all data from file_data"""

        raise NotImplementedError

    # Access via model.py data
    # ------------------------

    def from_data_array(self, clear=True):
        """Replaces everything in file_data from data_array

        Parameters
        ----------
        clear: Bool, defaults to True
        \tIf True file_data is repaced. If false it is updated

        """

        if clear:
            self.clear_file_data()

        self.shape2pys()
        self.code2pys()
        self.attributes2pys()
        self.row_heights2pys()
        self.col_widths2pys()
        self.macros2pys()

    def to_data_array(self, clear=True):
        """Replaces everything in data_array from file_data

        Parameters
        ----------
        clear: Bool, defaults to True
        \tIf True file_data is repaced. If false it is updated

        """

        if clear:
            self.clear_data_array()

        self.pys2shape()
        self.pys2code()
        self.pys2attributes()
        self.pys2row_heights()
        self.pys2col_widths()
        self.pys2macros()

    def clear_data_array(self):
        """Removes all data from data_array"""

        raise NotImplementedError
