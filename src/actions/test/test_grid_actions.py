#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Martin Manns
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
test_grid_actions.py
====================

Unit tests for _grid_actions.py

"""

import os
from sys import path

test_path = os.path.dirname(os.path.realpath(__file__))
path.insert(0, test_path + "/../..")

import bz2
import wx
app = wx.App()

from lib.selection import Selection

from lib.testlib import main_window, grid, code_array, grid_values, _fill_grid
from lib.testlib import params, pytest_generate_tests

from gui._events import *

class TestFileActions(object):
    """File actions test class"""

    def setup_method(self, method):
        
        # Filenames
        # ---------
        
        # File with valid signature
        self.filename_valid_sig = "test1.pys"
        
        # File without signature
        self.filename_no_sig = "test2.pys"
        
        # File with invalid signature
        self.filename_invalid_sig = "test3.pys"
        
        # File for grid size test
        self.filename_gridsize = "test4.pys"
        
        # Empty file
        self.filename_empty = "test5.pys"
        
        # File name that cannot be accessed
        self.filename_not_permitted = "test6.pys"
        
        # File name without file
        self.filename_wrong = "test-1.pys"
        
        # File for testing save
        self.filename_save = "test_save.pys"
        
    def test_validate_signature(self):
        """Tests signature validation"""
        
        # Test missing sig file
        assert not grid.actions.validate_signature(self.filename_no_sig)
        
        # Test valid sig file
        assert grid.actions.validate_signature(self.filename_valid_sig)
        
        # Test invalid sig file
        assert not \
            grid.actions.validate_signature(self.filename_invalid_sig)
        
    def test_enter_safe_mode(self):
        """Tests safe mode entry"""
        
        grid.actions.leave_safe_mode()
        grid.actions.enter_safe_mode()
        assert grid.code_array.safe_mode

    def test_leave_safe_mode(self):
        """Tests save mode exit"""
        
        grid.actions.enter_safe_mode()
        grid.actions.leave_safe_mode()
        assert not grid.code_array.safe_mode

    def test_approve(self):
        
        # Test if safe_mode is correctly set for invalid sig
        grid.actions.approve(self.filename_invalid_sig)
        
        assert grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for valid sig
        
        grid.actions.approve(self.filename_valid_sig)
            
        assert not grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for missing sig
        grid.actions.approve(self.filename_no_sig)
        
        assert grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for io-error sig
        
        os.chmod(self.filename_not_permitted, 0200)
        os.chmod(self.filename_not_permitted + ".sig", 0200)
        
        grid.actions.approve(self.filename_not_permitted)
        
        assert grid.GetTable().data_array.safe_mode
        
        os.chmod(self.filename_not_permitted, 0644)
        os.chmod(self.filename_not_permitted + ".sig", 0644)
    
    def test_get_file_version(self):
        """Tests infile version string."""
        
        infile = bz2.BZ2File(self.filename_valid_sig)
        version = grid.actions._get_file_version(infile)
        assert version == "0.1"
        infile.close()
    
    def test_clear(self):
        """Tests empty_grid method"""
        
        # Set up grid
        
        grid.code_array[(0, 0, 0)] = "'Test1'"
        grid.code_array[(3, 1, 1)] = "'Test2'"
        
        grid.actions.set_col_width(1, 23)
        grid.actions.set_col_width(0, 233)
        grid.actions.set_row_height(0, 0)
        
        selection = Selection([],[],[],[],[(0, 0)])
        grid.actions.set_attr("bgcolor", wx.RED, selection)
        grid.actions.set_attr("frozen", "print 'Testcode'", selection)
        
        # Clear grid
        
        grid.actions.clear()
        
        # Code content
        
        assert grid.code_array((0, 0, 0)) is None
        assert grid.code_array((3, 1, 1)) is None
        
        assert list(grid.code_array[:2, 0, 0]) == [None, None]
        
        # Cell attributes
        cell_attributes = grid.code_array.cell_attributes
        assert cell_attributes == []
        
        # Row heights and column widths
        
        row_heights = grid.code_array.row_heights
        assert len(row_heights) == 0
        
        col_widths = grid.code_array.col_widths
        assert len(col_widths) == 0
        
        # Undo and redo
        undolist = grid.code_array.unredo.undolist
        redolist = grid.code_array.unredo.redolist
        assert undolist == []
        assert redolist == []
        
        # Caches
        
        # Clear grid again because lookup is added in resultcache
        
        grid.actions.clear()
        
        result_cache = grid.code_array.result_cache
        assert len(result_cache) == 0
    
    def test_open(self):
        """Tests open functionality"""

        class Event(object):
            attr = {}
        event = Event()
        
        # Test missing file
        event.attr["filepath"] = self.filename_wrong
        
        assert not grid.actions.open(event)
        
        # Test unaccessible file
        os.chmod(self.filename_not_permitted, 0200)
        event.attr["filepath"] = self.filename_not_permitted
        assert not grid.actions.open(event)
        
        os.chmod(self.filename_not_permitted, 0644)
        
        # Test empty file
        event.attr["filepath"] = self.filename_empty
        assert not grid.actions.open(event)
        
        assert grid.GetTable().data_array.safe_mode # sig is also empty
        
        # Test invalid sig files
        event.attr["filepath"] = self.filename_invalid_sig
        grid.actions.open(event)
        
        assert grid.GetTable().data_array.safe_mode
        
        # Test file with sig
        event.attr["filepath"] = self.filename_valid_sig
        grid.actions.open(event)
            
        assert not grid.GetTable().data_array.safe_mode
        
        # Test file without sig
        event.attr["filepath"] = self.filename_no_sig
        grid.actions.open(event)
        
        assert grid.GetTable().data_array.safe_mode
        
        # Test grid size for valid file
        event.attr["filepath"] = self.filename_gridsize
        grid.actions.open(event)
        
        assert not grid.GetTable().data_array.safe_mode
        new_shape = grid.GetTable().data_array.shape
        assert new_shape == (1000, 100, 10)
        
        # Test grid content for valid file
        
        assert grid.GetTable().data_array[0, 0, 0] == "test4"
    
    def test_save(self):
        """Tests save functionality"""
        
        class Event(object):
            attr = {}
        event = Event()
        
        # Test normal save
        event.attr["filepath"] = self.filename_save
        
        grid.actions.save(event)
        
        savefile = open(self.filename_save)
        
        assert savefile
        savefile.close()
        
        # Test double filename
        
        grid.actions.save(event)
        
        # Test io error
        
        os.chmod(self.filename_save, 0200)
        try:
            grid.actions.save(event)
            raise IOError, "No error raised even though target not writable"
        except IOError:
            pass
        os.chmod(self.filename_save, 0644)
        
        # Test invalid file name
        
        event.attr["filepath"] = None
        try:
            grid.actions.save(event)
            raise TypeError, "None accepted as filename"
        except TypeError:
            pass
        
        # Test sig creation is happening
        
        sigfile = open(self.filename_save + ".sig")
        assert sigfile
        sigfile.close()
        
        os.remove(self.filename_save)
        os.remove(self.filename_save + ".sig")

    def test_sign_file(self):
        """Tests signing functionality"""
        
        os.remove(self.filename_valid_sig + ".sig")
        grid.actions.sign_file(self.filename_valid_sig)
        dirlist = os.listdir(".")
        assert self.filename_valid_sig + ".sig" in dirlist

class TestTableRowActionsMixins(object):
    """Unit test class for TableRowActionsMixins"""
    
    param_set_row_height = [ \
        {'row': 0, 'tab': 0, 'height': 0},
        {'row': 0, 'tab': 1, 'height': 0},
        {'row': 0, 'tab': 0, 'height': 34},
        {'row': 10, 'tab': 12, 'height': 3245.78},
    ]
    
    @params(param_set_row_height)
    def test_set_row_height(self, row, tab, height):
        grid.current_table = tab
        grid.actions.set_row_height(row, height)
        row_heights = grid.code_array.row_heights
        assert row_heights[row, tab] == height
    
    param_insert_rows = [ \
        {'row': 0, 'no_rows': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'row': 0, 'no_rows': 1, 'test_key': (0, 0, 0), 'test_val': None},
        {'row': 0, 'no_rows': 1, 'test_key': (1, 0, 0), 'test_val': "'Test'"},
        {'row': 0, 'no_rows': 5, 'test_key': (5, 0, 0), 'test_val': "'Test'"},
        {'row': 1, 'no_rows': 1, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'row': 1, 'no_rows': 1, 'test_key': (1, 0, 0), 'test_val': None},
        {'row': 1, 'no_rows': 1, 'test_key': (2, 1, 0), 'test_val': "3"},
        {'row': 1, 'no_rows': 5000, 'test_key': (5001, 1, 0), 'test_val': "3"},
    ]
    
    @params(param_insert_rows)
    def test_insert_rows(self, row, no_rows, test_key, test_val):
        # Set up grid
        grid.actions.clear((1000, 100, 3))
        _fill_grid(grid_values)
        
        # Insert and test
        grid.actions.insert_rows(row, no_rows=no_rows)
        assert grid.code_array(test_key) == test_val

    param_delete_rows = [ \
       {'row': 0, 'no_rows': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'row': 0, 'no_rows': 1, 'test_key': (0, 0, 0), 'test_val': None},
       {'row': 0, 'no_rows': 1, 'test_key': (0, 1, 0), 'test_val': "3"},
       {'row': 0, 'no_rows': 995, 'test_key': (4, 99, 0), 'test_val': "$^%&$^"},
       {'row': 1, 'no_rows': 1, 'test_key': (0, 1, 0), 'test_val': "1"},
       {'row': 1, 'no_rows': 1, 'test_key': (1, 1, 0), 'test_val': None},
       {'row': 1, 'no_rows': 999, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
    ]

    @params(param_delete_rows)
    def test_delete_rows(self, row, no_rows, test_key, test_val):
        # Set up grid
        grid.actions.clear((1000, 100, 3))
        _fill_grid(grid_values)
        
        # Delete and test
        grid.actions.delete_rows(row, no_rows=no_rows)
        assert grid.code_array(test_key) == test_val
        

class TestTableColumnActionsMixin(object):
    """Unit test class for TableColumnActionsMixin"""
        
    param_set_col_width = [ \
        {'col': 0, 'tab': 0, 'width': 0},
        {'col': 0, 'tab': 1, 'width': 0},
        {'col': 0, 'tab': 0, 'width': 34},
        {'col': 10, 'tab': 12, 'width': 3245.78},
    ]
    
    @params(param_set_col_width)
    def test_set_col_width(self, col, tab, width):
        grid.current_table = tab
        grid.actions.set_col_width(col, width)
        col_widths = grid.code_array.col_widths
        assert col_widths[col, tab] == width
        
    param_insert_cols = [ \
        {'col': 0, 'no_cols': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'col': 0, 'no_cols': 1, 'test_key': (0, 0, 0), 'test_val': None},
        {'col': 0, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': "'Test'"},
        {'col': 0, 'no_cols': 5, 'test_key': (0, 5, 0), 'test_val': "'Test'"},
        {'col': 1, 'no_cols': 1, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'col': 1, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': None},
        {'col': 1, 'no_cols': 1, 'test_key': (1, 2, 0), 'test_val': "3"},
        {'col': 1, 'no_cols': 5000, 'test_key': (1, 5001, 0), 'test_val': "3"},
    ]
    
    @params(param_insert_cols)
    def test_insert_cols(self, col, no_cols, test_key, test_val):
        # Set up grid
        grid.actions.clear((1000, 100, 3))
        _fill_grid(grid_values)
        
        # Insert and test
        grid.actions.insert_cols(col, no_cols=no_cols)
        assert grid.code_array(test_key) == test_val
        
    param_delete_cols = [ \
       {'col': 0, 'no_cols': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'col': 0, 'no_cols': 1, 'test_key': (0, 2, 0), 'test_val': None},
       {'col': 0, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': "2"},
       {'col': 0, 'no_cols': 95, 'test_key': (999, 4, 0), 'test_val': "$^%&$^"},
       {'col': 1, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': "2"},
       {'col': 1, 'no_cols': 1, 'test_key': (1, 1, 0), 'test_val': "4"},
       {'col': 1, 'no_cols': 99, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
    ]

    @params(param_delete_cols)
    def test_delete_cols(self, col, no_cols, test_key, test_val):
        # Set up grid
        grid.actions.clear((1000, 100, 3))
        _fill_grid(grid_values)
        
        # Delete and test
        grid.actions.delete_cols(col, no_cols=no_cols)
        assert grid.code_array(test_key) == test_val
        
    
class TestTableTabActionsMixin(object):
    """Unit test class for TableTabActionsMixin"""
    
    param_insert_tabs = [ \
        {'tab': 0, 'no_tabs': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'tab': 0, 'no_tabs': 1, 'test_key': (0, 0, 0), 'test_val': None},
        {'tab': 0, 'no_tabs': 1, 'test_key': (0, 0, 1), 'test_val': "'Test'"},
        {'tab': 0, 'no_tabs': 5, 'test_key': (0, 0, 5), 'test_val': "'Test'"},
        {'tab': 1, 'no_tabs': 1, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'tab': 1, 'no_tabs': 1, 'test_key': (0, 0, 1), 'test_val': None},
        {'tab': 1, 'no_tabs': 1, 'test_key': (1, 2, 3), 'test_val': "78"},
        {'tab': 1, 'no_tabs': 5000, 'test_key': (1, 2, 5002), 'test_val': "78"},
    ]
    
    @params(param_insert_tabs)
    def test_insert_tabs(self, tab, no_tabs, test_key, test_val):
        # Set up grid
        grid.actions.clear((1000, 100, 3))
        _fill_grid(grid_values)
        
        # Insert and test
        grid.actions.insert_tabs(tab, no_tabs=no_tabs)
        assert grid.code_array(test_key) == test_val
        
    param_delete_tabs = [ \
       {'tab': 0, 'no_tabs': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'tab': 0, 'no_tabs': 1, 'test_key': (0, 2, 0), 'test_val': None},
       {'tab': 0, 'no_tabs': 1, 'test_key': (1, 2, 1), 'test_val': "78"},
       {'tab': 2, 'no_tabs': 1, 'test_key': (1, 2, 1), 'test_val': None},
       {'tab': 1, 'no_tabs': 1, 'test_key': (1, 2, 1), 'test_val': "78"},
       {'tab': 0, 'no_tabs': 2, 'test_key': (1, 2, 0), 'test_val': "78"},
    ]

    @params(param_delete_tabs)
    def test_delete_tabs(self, tab, no_tabs, test_key, test_val):
        # Set up grid
        grid.actions.clear((1000, 100, 3))
        _fill_grid(grid_values)
        
        # Delete and test
        grid.actions.delete_tabs(tab, no_tabs=no_tabs)
        assert grid.code_array(test_key) == test_val

class TestTableActions(object):
        
    def test_paste(self):
        """Tests paste into grid"""
        
        # Test 1D paste of strings
        tl_cell = 0, 0, 0
        data = [map(str, [1, 2, 3, 4]), [""] * 4]
        
        grid.actions.paste(tl_cell, data)
        
        assert grid.code_array[tl_cell] == 1
        assert grid.code_array(tl_cell) == '1'
        assert grid.code_array[0, 1, 0] == 2
        assert grid.code_array[0, 2, 0] == 3
        assert grid.code_array[0, 3, 0] == 4
        
        # Test row overflow
        ##TODO
        
        # Test col overflow
        ##TODO
    
    def test_on_key(self):
        pass
        
    def test_change_grid_shape(self):
        pass


class TestUnRedoActions(object):
    def test_undo(self):
        pass
        
    def test_redo(self):
        pass
        


class TestGridActions(object):
    """Grid level grid actions test class"""
    
    def setup_method(self, method):
        class Event(object):
            pass
            
        self.event = Event()
        
    def test_new(self):
        """Tests creation of a new spreadsheets"""
        
        dims = [1, 1, 1, 10, 1, 1, 1, 10, 1, 1, 1, 10, 10, 10, 10]
        dims = zip(dims[::3], dims[1::3], dims[2::3])
        
        for dim in dims:
            self.event.shape = dim
            grid.actions.new(self.event)
            new_shape = grid.GetTable().data_array.shape
            assert new_shape == dim
            
    def test_get_visible_area(self):
        pass
        
    def test_switch_to_table(self):
        pass
        
    def test_get_cursor(self):
        pass
        
    def test_set_cursor(self):
        pass
        

class TestSelectionActions(object):
    """Selection actions test class"""
    
    def test_get_selection(self):
        pass
        
    def test_select_cell(self):
        pass
        
    def test_select_slice(self):
        pass
        
    def test_delete_selection(self):
        pass
    
    
class TestFindActions(object):
    """FindActions test class"""
    
    def test_find(self):
        pass
        
    def test_replace(self):
        pass

    
    
