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

from gui._main_window import MainWindow
from gui._grid import Grid
from lib.selection import Selection
from lib.testlib import params, pytest_generate_tests
import actions._grid_actions
from model.model import CodeArray

from gui._events import *

class TestFileActions(object):
    """File actions test class"""

    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid
        
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
        assert not self.grid.actions.validate_signature(self.filename_no_sig)
        
        # Test valid sig file
        assert self.grid.actions.validate_signature(self.filename_valid_sig)
        
        # Test invalid sig file
        assert not \
            self.grid.actions.validate_signature(self.filename_invalid_sig)
        
    def test_enter_safe_mode(self):
        """Tests safe mode entry"""
        
        self.grid.actions.leave_safe_mode()
        self.grid.actions.enter_safe_mode()
        assert self.grid.code_array.safe_mode

    def test_leave_safe_mode(self):
        """Tests save mode exit"""
        
        self.grid.actions.enter_safe_mode()
        self.grid.actions.leave_safe_mode()
        assert not self.grid.code_array.safe_mode

    def test_approve(self):
        
        # Test if safe_mode is correctly set for invalid sig
        self.grid.actions.approve(self.filename_invalid_sig)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for valid sig
        
        self.grid.actions.approve(self.filename_valid_sig)
            
        assert not self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for missing sig
        self.grid.actions.approve(self.filename_no_sig)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for io-error sig
        
        os.chmod(self.filename_not_permitted, 0200)
        os.chmod(self.filename_not_permitted + ".sig", 0200)
        
        self.grid.actions.approve(self.filename_not_permitted)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        os.chmod(self.filename_not_permitted, 0644)
        os.chmod(self.filename_not_permitted + ".sig", 0644)
    
    def test_get_file_version(self):
        """Tests infile version string."""
        
        infile = bz2.BZ2File(self.filename_valid_sig)
        version = self.grid.actions._get_file_version(infile)
        assert version == "0.1"
        infile.close()
    
    def test_clear(self):
        """Tests empty_grid method"""
        
        # Set up grid
        
        self.grid.code_array[(0, 0, 0)] = "'Test1'"
        self.grid.code_array[(3, 1, 1)] = "'Test2'"
        
        self.grid.actions.set_col_width(1, 23)
        self.grid.actions.set_col_width(0, 233)
        self.grid.actions.set_row_height(0, 0)
        
        selection = Selection([],[],[],[],[(0, 0)])
        self.grid.actions.set_attr("bgcolor", wx.RED, selection)
        self.grid.actions.set_attr("frozen", "print 'Testcode'", selection)
        
        # Clear grid
        
        self.grid.actions.clear()
        
        # Code content
        
        assert self.grid.code_array((0, 0, 0)) is None
        assert self.grid.code_array((3, 1, 1)) is None
        
        assert list(self.grid.code_array[:2, 0, 0]) == [None, None]
        
        # Cell attributes
        cell_attributes = self.grid.code_array.cell_attributes
        assert cell_attributes == []
        
        # Row heights and column widths
        
        row_heights = self.grid.code_array.row_heights
        assert len(row_heights) == 0
        
        col_widths = self.grid.code_array.col_widths
        assert len(col_widths) == 0
        
        # Undo and redo
        undolist = self.grid.code_array.unredo.undolist
        redolist = self.grid.code_array.unredo.redolist
        assert undolist == []
        assert redolist == []
        
        # Caches
        
        # Clear grid again because lookup is added in resultcache
        
        self.grid.actions.clear()
        
        result_cache = self.grid.code_array.result_cache
        assert len(result_cache) == 0
    
    def test_open(self):
        """Tests open functionality"""

        class Event(object):
            attr = {}
        event = Event()
        
        # Test missing file
        event.attr["filepath"] = self.filename_wrong
        
        assert not self.grid.actions.open(event)
        
        # Test unaccessible file
        os.chmod(self.filename_not_permitted, 0200)
        event.attr["filepath"] = self.filename_not_permitted
        assert not self.grid.actions.open(event)
        
        os.chmod(self.filename_not_permitted, 0644)
        
        # Test empty file
        event.attr["filepath"] = self.filename_empty
        assert not self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode # sig is also empty
        
        # Test invalid sig files
        event.attr["filepath"] = self.filename_invalid_sig
        self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test file with sig
        event.attr["filepath"] = self.filename_valid_sig
        self.grid.actions.open(event)
            
        assert not self.grid.GetTable().data_array.safe_mode
        
        # Test file without sig
        event.attr["filepath"] = self.filename_no_sig
        self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test grid size for valid file
        event.attr["filepath"] = self.filename_gridsize
        self.grid.actions.open(event)
        
        assert not self.grid.GetTable().data_array.safe_mode
        new_shape = self.grid.GetTable().data_array.shape
        assert new_shape == (1000, 100, 10)
        
        # Test grid content for valid file
        
        assert self.grid.GetTable().data_array[0, 0, 0] == "test4"
    
    def test_save(self):
        """Tests save functionality"""
        
        class Event(object):
            attr = {}
        event = Event()
        
        # Test normal save
        event.attr["filepath"] = self.filename_save
        
        self.grid.actions.save(event)
        
        savefile = open(self.filename_save)
        
        assert savefile
        savefile.close()
        
        # Test double filename
        
        self.grid.actions.save(event)
        
        # Test io error
        
        os.chmod(self.filename_save, 0200)
        try:
            self.grid.actions.save(event)
            raise IOError, "No error raised even though target not writable"
        except IOError:
            pass
        os.chmod(self.filename_save, 0644)
        
        # Test invalid file name
        
        event.attr["filepath"] = None
        try:
            self.grid.actions.save(event)
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
        self.grid.actions.sign_file(self.filename_valid_sig)
        dirlist = os.listdir(".")
        assert self.filename_valid_sig + ".sig" in dirlist

class TestTableRowActionsMixins(object):
    """Unit test class for TableRowActionsMixins"""
    
    main_window = MainWindow(None, -1)
    grid = main_window.grid
    
    param_set_row_height = [ \
        {'row': 0, 'tab': 0, 'height': 0},
        {'row': 0, 'tab': 1, 'height': 0},
        {'row': 0, 'tab': 0, 'height': 34},
        {'row': 10, 'tab': 12, 'height': 3245.78},
    ]
    
    @params(param_set_row_height)
    def test_set_row_height(self, row, tab, height):
        self.grid.current_table = tab
        self.grid.actions.set_row_height(row, height)
        row_heights = self.grid.code_array.row_heights
        assert row_heights[row, tab] == height
        
    def test_insert_rows(self):
        self.grid.code_array[(1, 0, 0)] = "42"
        
        # Insert 1 row at row 0
        self.grid.actions.insert_rows(0)
        assert self.grid.code_array[(1, 0, 0)] is None
        assert self.grid.code_array[(2, 0, 0)] == 42
        
        # Insert 3 rows at row 1
        self.grid.actions.insert_rows(1, no_rows=3)
        assert self.grid.code_array[(2, 0, 0)] is None
        assert self.grid.code_array[(5, 0, 0)] == 42
        
    def test_delete_rows(self):
        pass
        

class TestTableColumnActionsMixin(object):
    """Unit test class for TableColumnActionsMixin"""
    
    main_window = MainWindow(None, -1)
    grid = main_window.grid
    
    param_set_col_width = [ \
        {'col': 0, 'tab': 0, 'width': 0},
        {'col': 0, 'tab': 1, 'width': 0},
        {'col': 0, 'tab': 0, 'width': 34},
        {'col': 10, 'tab': 12, 'width': 3245.78},
    ]
    
    @params(param_set_col_width)
    def test_set_col_width(self, col, tab, width):
        self.grid.current_table = tab
        self.grid.actions.set_col_width(col, width)
        col_widths = self.grid.code_array.col_widths
        assert col_widths[col, tab] == width
        
    def test_insert_cols(self):
        pass
        
    def test_delete_cols(self):
        pass
        
    
class TestTableTabActionsMixin(object):
    def test_insert_tabs(self):
        pass
        
    def test_delete_tabs(self):
        pass

class TestTableActions(object):
    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid
        
    def test_paste(self):
        """Tests paste into grid"""
        
        # Test 1D paste of strings
        tl_cell = 0, 0, 0
        data = [map(str, [1, 2, 3, 4]), [""] * 4]
        
        self.grid.actions.paste(tl_cell, data)
        
        assert self.grid.code_array[tl_cell] == 1
        assert self.grid.code_array(tl_cell) == '1'
        assert self.grid.code_array[0, 1, 0] == 2
        assert self.grid.code_array[0, 2, 0] == 3
        assert self.grid.code_array[0, 3, 0] == 4
        
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
        main_window = MainWindow(None, -1)
        self.grid = main_window.grid
        
        class Event(object):
            pass
            
        self.event = Event()
        
    def test_new(self):
        """Tests creation of a new spreadsheets"""
        
        dims = [1, 1, 1, 10, 1, 1, 1, 10, 1, 1, 1, 10, 10, 10, 10]
        dims = zip(dims[::3], dims[1::3], dims[2::3])
        
        for dim in dims:
            self.event.shape = dim
            self.grid.actions.new(self.event)
            new_shape = self.grid.GetTable().data_array.shape
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

    
    
