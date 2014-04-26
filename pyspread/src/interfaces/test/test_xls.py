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
test_xls
========

Unit tests for xls.py

"""

raise NotImplementedError

import bz2
import os
import sys

import xlrd

from src.interfaces.xls import Xls
from src.lib.selection import Selection
from src.lib.testlib import params, pytest_generate_tests
from src.model.model import CodeArray

TESTPATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-1]) + os.sep
sys.path.insert(0, TESTPATH)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 3)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 2)


class TestXls(object):
    """Unit tests for Xls"""

    def setup_method(self, method):
        """Creates Xls class with code_array and temporary test.xls file"""

        # All data structures are initially empty
        # The test file xls_file has entries in each category

        self.code_array = CodeArray((1000, 100, 3))
        self.xls_infile = xlrd.open_workbook(TESTPATH + "xls_test1.xls",
                                             formatting_info=True)
        self.xls_outfile_path = TESTPATH + "xls_test2.xls"
        self.xls_in = Xls(self.code_array, self.xls_infile)

    def write_xls_out(self, method_name, *args, **kwargs):
        """Helper that writes an xls_out file"""

        workbook = xlwt.Workbook()

        xls_out = Xls(self.code_array, workbook)
        method = getattr(xls_out, method_name)
        method(*args, **kwargs)
        workbook.save(self.xls_outfile_path)

    def read_xls_out(self):
        """Returns string of xls_out content and removes xls_out"""

        out_workbook = xlrd.open_workbook(self.xls_outfile_path,
                                          formatting_info=True)

        # Clean up the test dir
        os.remove(self.xls_outfile_path)

        return out_workbook

    param_idx2colour = [
        {'string': "1", 'maxsplit': None, 'res': ["1"]},
        {'string': "1\t2", 'maxsplit': None, 'res': ["1", "2"]},
        {'string': "1\t2\n", 'maxsplit': None, 'res': ["1", "2"]},
        {'string': "1\t2\t3", 'maxsplit': 1, 'res': ["1", "2\t3"]},
        {'string': "1\t2\t3\n", 'maxsplit': 1, 'res': ["1", "2\t3"]},
    ]

    @params(param_idx2colour)
    def test_idx2colour(self, string, maxsplit, res):
        """Test idx2colour method"""

        assert self.xls_in._split_tidy(string, maxsplit) == res

    param_color2idx = [
        {'keystrings': ["1", "2", "3"], 'res': (1, 2, 3)},
        {'keystrings': ["0", "0", "0"], 'res': (0, 0, 0)},
        {'keystrings': ["0", "0"], 'res': (0, 0)},
        {'keystrings': ["-2", "-2", "23"], 'res': (-2, -2, 23)},
        {'keystrings': map(str, xrange(100)), 'res': tuple(xrange(100))},
        {'keystrings': map(unicode, xrange(100)), 'res': tuple(xrange(100))},
    ]

    @params(param_color2idx)
    def test_color2idx(self, keystrings, res):
        """Test color2idx method"""

        assert self.xls_in._get_key(*keystrings) == res

    param_shape2xls = [
        {'shape': (1000, 100, 3), 'res': "1000\t100\t3\n"},
        {'shape': (1, 1, 1), 'res': "1\t1\t1\n"},
        {'shape': (1000000, 1000000, 2), 'res': "1000000\t1000000\t2\n"},
    ]

    @params(param_shape2xls)
    def test_shape2xls(self, shape, res):
        """Test _shape2xls method"""

        self.code_array.dict_grid.shape = shape
        self.write_xls_out("_shape2xls")
        assert self.read_xls_out() == res

    @params(param_shape2xls)
    def test_xls2shape(self, res, shape):
        """Test _xls2shape method"""

        self.xls_in._xls2shape(res)
        assert self.code_array.dict_grid.shape == shape

    param_code2xls = [
        {'code': "0\t0\t0\tTest\n", 'key': (0, 0, 0), 'val': "Test"},
        {'code': "10\t0\t0\t" + u"öäüß".encode("utf-8") + "\n",
         'key': (10, 0, 0), 'val': u"öäüß"},
        {'code': "2\t0\t0\tTest\n", 'key': (2, 0, 0), 'val': "Test"},
        {'code': "2\t0\t0\t" + "a" * 100 + '\n', 'key': (2, 0, 0),
         'val': "a" * 100},
        {'code': '0\t0\t0\t"Test"\n', 'key': (0, 0, 0), 'val': '"Test"'},
    ]

    @params(param_code2xls)
    def test_code2xls(self, key, val, code):
        """Test _code2xls method"""

        self.code_array[key] = val
        self.write_xls_out("_code2xls")
        res = self.read_xls_out()

        assert res == code

    @params(param_code2xls)
    def test_xls2code(self, val, code, key):
        """Test _xls2code method"""

        self.xls_in._xls2code(code)
        assert self.code_array(key) == val

    param_attributes2xls = [
        {'code': "[]\t[]\t[]\t[]\t[(3, 4)]\t0\t'borderwidth_bottom'\t42\n",
         'selection': Selection([], [], [], [], [(3, 4)]), 'table': 0,
         'key': (3, 4, 0), 'attr': 'borderwidth_bottom', 'val': 42},
    ]

    param_get_font = [
        {'code': "0\t0\t0\tTest\n", 'key': (0, 0, 0), 'val': "Test"},
        {'code': "10\t0\t0\t" + u"öäüß".encode("utf-8") + "\n",
         'key': (10, 0, 0), 'val': u"öäüß"},
        {'code': "2\t0\t0\tTest\n", 'key': (2, 0, 0), 'val': "Test"},
        {'code': "2\t0\t0\t" + "a" * 100 + '\n', 'key': (2, 0, 0),
         'val': "a" * 100},
        {'code': '0\t0\t0\t"Test"\n', 'key': (0, 0, 0), 'val': '"Test"'},
    ]

    @params(param_get_font)
    def test_get_font(self, key, val, code):
        """Test _get_font method"""

        self.code_array[key] = val
        self.write_xls_out("_code2xls")
        res = self.read_xls_out()

        assert res == code

    param_get_alignment = [
        {'code': "0\t0\t0\tTest\n", 'key': (0, 0, 0), 'val': "Test"},
        {'code': "10\t0\t0\t" + u"öäüß".encode("utf-8") + "\n",
         'key': (10, 0, 0), 'val': u"öäüß"},
        {'code': "2\t0\t0\tTest\n", 'key': (2, 0, 0), 'val': "Test"},
        {'code': "2\t0\t0\t" + "a" * 100 + '\n', 'key': (2, 0, 0),
         'val': "a" * 100},
        {'code': '0\t0\t0\t"Test"\n', 'key': (0, 0, 0), 'val': '"Test"'},
    ]

    @params(param_get_alignment)
    def test_get_alignment(self, key, val, code):
        """Test _get_alignment method"""

        self.code_array[key] = val
        self.write_xls_out("_code2xls")
        res = self.read_xls_out()

        assert res == code

    param_get_pattern = [
        {'code': "0\t0\t0\tTest\n", 'key': (0, 0, 0), 'val': "Test"},
        {'code': "10\t0\t0\t" + u"öäüß".encode("utf-8") + "\n",
         'key': (10, 0, 0), 'val': u"öäüß"},
        {'code': "2\t0\t0\tTest\n", 'key': (2, 0, 0), 'val': "Test"},
        {'code': "2\t0\t0\t" + "a" * 100 + '\n', 'key': (2, 0, 0),
         'val': "a" * 100},
        {'code': '0\t0\t0\t"Test"\n', 'key': (0, 0, 0), 'val': '"Test"'},
    ]

    @params(param_get_pattern)
    def test_get_pattern(self, key, val, code):
        """Test _get_pattern method"""

        self.code_array[key] = val
        self.write_xls_out("_code2xls")
        res = self.read_xls_out()

        assert res == code

    param_get_borders = [
        {'code': "0\t0\t0\tTest\n", 'key': (0, 0, 0), 'val': "Test"},
        {'code': "10\t0\t0\t" + u"öäüß".encode("utf-8") + "\n",
         'key': (10, 0, 0), 'val': u"öäüß"},
        {'code': "2\t0\t0\tTest\n", 'key': (2, 0, 0), 'val': "Test"},
        {'code': "2\t0\t0\t" + "a" * 100 + '\n', 'key': (2, 0, 0),
         'val': "a" * 100},
        {'code': '0\t0\t0\t"Test"\n', 'key': (0, 0, 0), 'val': '"Test"'},
    ]

    @params(param_get_borders)
    def test_get_borders(self, key, val, code):
        """Test _get_borders method"""

        self.code_array[key] = val
        self.write_xls_out("_code2xls")
        res = self.read_xls_out()

        assert res == code

    param_get_xfstyle = [
        {'code': "0\t0\t0\tTest\n", 'key': (0, 0, 0), 'val': "Test"},
        {'code': "10\t0\t0\t" + u"öäüß".encode("utf-8") + "\n",
         'key': (10, 0, 0), 'val': u"öäüß"},
        {'code': "2\t0\t0\tTest\n", 'key': (2, 0, 0), 'val': "Test"},
        {'code': "2\t0\t0\t" + "a" * 100 + '\n', 'key': (2, 0, 0),
         'val': "a" * 100},
        {'code': '0\t0\t0\t"Test"\n', 'key': (0, 0, 0), 'val': '"Test"'},
    ]

    @params(param_get_xfstyle)
    def test_get_xfstyle(self, key, val, code):
        """Test _get_xfstyle method"""

        self.code_array[key] = val
        self.write_xls_out("_code2xls")
        res = self.read_xls_out()

        assert res == code

    @params(param_attributes2xls)
    def test_xls2attributes(self, selection, table, key, attr, val, code):
        """Test _xls2attributes method"""

        self.xls_in._xls2attributes(code)

        attrs = self.code_array.dict_grid.cell_attributes[key]
        assert attrs[attr] == val

    param_cell_attribute_append = [
        {'row': 0, 'tab': 0, 'height': 0.1, 'code': "0\t0\t0.1\n"},
        {'row': 0, 'tab': 0, 'height': 0.0, 'code': "0\t0\t0.0\n"},
        {'row': 10, 'tab': 0, 'height': 1.0, 'code': "10\t0\t1.0\n"},
        {'row': 10, 'tab': 10, 'height': 1.0, 'code': "10\t10\t1.0\n"},
        {'row': 10, 'tab': 10, 'height': 100.0, 'code': "10\t10\t100.0\n"},
    ]

    @params(param_cell_attribute_append)
    def test_cell_attribute_append(self, selection, table, key, attr, val,
                                   code):
        """Test _cell_attribute_append method"""

        self.code_array.dict_grid.cell_attributes.undoable_append(
            (selection, table, {attr: val}), mark_unredo=False)

        self.write_xls_out("_attributes2xls")
        assert self.read_xls_out() == code

    param_row_heights2xls = [
        {'row': 0, 'tab': 0, 'height': 0.1, 'code': "0\t0\t0.1\n"},
        {'row': 0, 'tab': 0, 'height': 0.0, 'code': "0\t0\t0.0\n"},
        {'row': 10, 'tab': 0, 'height': 1.0, 'code': "10\t0\t1.0\n"},
        {'row': 10, 'tab': 10, 'height': 1.0, 'code': "10\t10\t1.0\n"},
        {'row': 10, 'tab': 10, 'height': 100.0, 'code': "10\t10\t100.0\n"},
    ]

    @params(param_row_heights2xls)
    def test_row_heights2xls(self, row, tab, height, code):
        """Test _row_heights2xls method"""

        self.code_array.dict_grid.row_heights[(row, tab)] = height
        self.write_xls_out("_row_heights2xls")
        assert self.read_xls_out() == code

    @params(param_row_heights2xls)
    def test_xls2row_heights(self, row, tab, height, code):
        """Test _xls2row_heights method"""

        self.xls_in._xls2row_heights(code)
        assert self.code_array.dict_grid.row_heights[(row, tab)] == height

    param_col_widths2xls = [
        {'col': 0, 'tab': 0, 'width': 0.1, 'code': "0\t0\t0.1\n"},
        {'col': 0, 'tab': 0, 'width': 0.0, 'code': "0\t0\t0.0\n"},
        {'col': 10, 'tab': 0, 'width': 1.0, 'code': "10\t0\t1.0\n"},
        {'col': 10, 'tab': 10, 'width': 1.0, 'code': "10\t10\t1.0\n"},
        {'col': 10, 'tab': 10, 'width': 100.0, 'code': "10\t10\t100.0\n"},
    ]

    @params(param_col_widths2xls)
    def test_col_widths2xls(self, col, tab, width, code):
        """Test _col_widths2xls method"""

        self.code_array.dict_grid.col_widths[(col, tab)] = width
        self.write_xls_out("_col_widths2xls")
        assert self.read_xls_out() == code

    @params(param_col_widths2xls)
    def test_xls2col_widths(self, col, tab, width, code):
        """Test _xls2col_widths method"""

        self.xls_in._xls2col_widths(code)
        assert self.code_array.dict_grid.col_widths[(col, tab)] == width

    def test_from_code_array(self):
        """Test from_code_array method"""

        self.xls_infile.seek(0)
        self.xls_in.to_code_array()

        outfile = bz2.BZ2File(self.xls_outfile_path, "w")
        xls_out = Xls(self.code_array, outfile)
        xls_out.from_code_array()
        outfile.close()

        self.xls_infile.seek(0)
        in_data = self.xls_infile.read()

        outfile = bz2.BZ2File(self.xls_outfile_path)
        out_data = outfile.read()
        outfile.close()

        # Clean up the test dir
        os.remove(self.xls_outfile_path)

        assert in_data == out_data

    def test_to_code_array(self):
        """Test to_code_array method"""

        self.xls_in.to_code_array()

        assert self.code_array((0, 0, 0)) == '"Hallo"'
