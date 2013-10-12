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
test_pys
========

Unit tests for pys.py

"""


class TestPys(object):
    """Unit tests for Pys"""

    def setup_method(self, method):
        """Creates Pys class with data_array and temporary test.pys file"""

        # All data structures are initially empty
        # The test file pys_file has entries in each category

        self.data_array = None
        self.pys_file = None

    def test_split_tidy(self):
        """Test _split_tidy method"""

    def test_get_key(self):
        """Test _get_key method"""

    def test_pys_assert_version(self):
        """Test _pys_assert_version method"""

    def test_version2pys(self):
        """Test _version2pys method"""

    def test_shape2pys(self):
        """Test _shape2pys method"""

    def test_pys2shape(self):
        """Test _pys2shape method"""

    def test_code2pys(self):
        """Test _code2pys method"""

    def test_pys2code(self):
        """Test _pys2code method"""

    def test_attributes2pys(self):
        """Test _attributes2pys method"""

    def test_pys2attributes(self):
        """Test _pys2attributes method"""

    def test_row_heights2pys(self):
        """Test _row_heights2pys method"""

    def test_pys2row_heights(self):
        """Test _pys2row_heights method"""

    def test_col_widths2pys(self):
        """Test _col_widths2pys method"""

    def test_pys2col_widths(self):
        """Test _pys2col_widths method"""

    def test_macros2pys(self):
        """Test _macros2pys method"""

    def test_pys2macros(self):
        """Test _pys2macros method"""

    def test_from_data_array(self):
        """Test from_data_array method"""

    def test_to_data_array(self):
        """Test to_data_array method"""
