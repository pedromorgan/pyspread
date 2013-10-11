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

from itertools import imap

class Pys(object):
    """Interface between data_array and pys file

    The pys file is read from disk with the read method.
    The pys file is written to disk with the write method.

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

    def read(self):
        """Read pys file to pys file data"""

    def write(self):
        """Write pys file to disk"""

    def shape2pys(self):
        """Updates shape in pys file data"""

    def pys2shape(self):
        """Updates shape in data_array"""

        shape_code = self.pys_file_data["shape"]
        self.data_array.shape = self._get_key(*self._split_tidy(shape_code))

    def code2pys(self):
        """Updates code in pys file data"""

    def pys2code(self):
        """Updates code in pys data_array"""

    def attributes2pys(self):
        """Updates attributes in pys file data"""

    def pys2attributes(self):
        """Updates attributes in data_array"""

    def row_heights2pys(self):
        """Updates row_heights in pys file data"""

    def pys2row_heights(self):
        """Updates row_heights in data_array"""

    def col_widths2pys(self):
        """Updates col_widths in pys file data"""

    def pys2col_widths(self):
        """Updates col_widths in data_array"""

    def macros2pys(self):
        """Updates macros in pys file data"""

        self.pys_file_data["macros"] = self.data_array.dict_grid.macros

    def pys2macros(self):
        """Updates macros in data_array"""

        self.data_array.dict_grid.macros = self.pys_file_data["macros"]

    def from_data_array(self):
        """Updates everything in pys file data"""

        self.shape2pys()
        self.code2pys()
        self.attributes2pys()
        self.row_heights2pys()
        self.col_widths2pys()
        self.macros2pys()

    def to_data_array(self):
        """Updates everything in data_array"""

        self.pys2shape()
        self.pys2code()
        self.pys2attributes()
        self.pys2row_heights()
        self.pys2col_widths()
        self.pys2macros()
