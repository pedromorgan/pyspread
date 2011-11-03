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
test_grid_cell_actions.py
=========================

Unit tests for _grid_sell_actions.py

"""

import os
from sys import path

test_path = os.path.dirname(os.path.realpath(__file__))
path.insert(0, test_path + "/../..")

import wx
app = wx.App()

from lib.selection import Selection

from lib.testlib import main_window, grid, code_array
from lib.testlib import params, pytest_generate_tests
from lib.testlib import basic_setup_test, restore_basic_grid

class TestCellActions(object):
    """Cell actions test class"""
    
    
    param_set_code = [ \
       {'key': (0, 0, 0), 'code': "'Test'", 'result': "'Test'"},
       {'key': (0, 0, 0), 'code': "", 'result': None},
       {'key': (0, 0, 1), 'code': None, 'result': None},
       {'key': (999, 99, 2), 'code': "4", 'result': "4"},
    ]

    @params(param_set_code)
    def test_set_code(self, key, code, result):
        """Unit test for set_code"""
        
        main_window.changed_since_save = False
        
        grid.actions.set_code(key, code)
        
        assert grid.code_array(key) == result
        
        wx.Yield()
        
        if code is None or not code:
            assert not main_window.changed_since_save
        else:
            assert main_window.changed_since_save
            
    
    @params(param_set_code)
    def test_delete_cell(self, key, code, result):
        """Unit test for delete_cell"""
        
        grid.actions.set_code(key, code)
        grid.actions.delete_cell(key)
        
        assert grid.code_array(key) is None
        
    param_get_reference = [ \
       {'cursor': (0, 0, 0), 'ref_key': (0, 0, 0), 'abs_ref': "S[0, 0, 0]",
        'rel_ref': "S[X, Y, Z]"},
       {'cursor': (0, 0, 1), 'ref_key': (0, 0, 1), 'abs_ref': "S[0, 0, 1]",
        'rel_ref': "S[X, Y, Z]"},
       {'cursor': (0, 0, 0), 'ref_key': (0, 0, 1), 'abs_ref': "S[0, 0, 1]",
        'rel_ref': "S[X, Y, Z+1]"},
       {'cursor': (9, 0, 0), 'ref_key': (0, 0, 0), 'abs_ref': "S[0, 0, 0]",
        'rel_ref': "S[X-9, Y, Z]"},
       {'cursor': (23, 2, 1), 'ref_key': (2, 2, 2), 'abs_ref': "S[2, 2, 2]",
        'rel_ref': "S[X-21, Y, Z+1]"},
    ]
        
    @params(param_get_reference)
    def test_get_absolute_reference(self, cursor, ref_key, abs_ref, rel_ref):
        """Unit test for _get_absolute_reference"""
        
        reference = grid.actions._get_absolute_reference(ref_key)
        
        assert reference == abs_ref
    
    @params(param_get_reference)
    def test_get_relative_reference(self, cursor, ref_key, abs_ref, rel_ref):
        """Unit test for _get_relative_reference"""
        
        reference = grid.actions._get_relative_reference(cursor, ref_key)
        
        assert reference == rel_ref
    
    @params(param_get_reference)
    def test_append_reference_code(self, cursor, ref_key, abs_ref, rel_ref):
        """Unit test for append_reference_code"""
        
        params = [
            # Normal initial code, absolute reference
            {'initial_code': "3 + ", 'ref_type': "absolute", 
             "res": grid.actions._get_absolute_reference(ref_key)},
            # Normal initial code, relative reference
            {'initial_code': "3 + ", 'ref_type': "relative", 
             "res": grid.actions._get_relative_reference(cursor, ref_key)},
            # Initial code with reference, absolute reference
            {'initial_code': "3 + S[2, 3, 1]", 'ref_type': "absolute", 
             "res": grid.actions._get_absolute_reference(ref_key)},
            # Initial code with reference, relative reference
            {'initial_code': "3 + S[2, 3, 1]", 'ref_type': "relative", 
             "res": grid.actions._get_relative_reference(cursor, ref_key)},
        ]
        
        for param in params:
            initial_code = param['initial_code'] 
            ref_type = param['ref_type']
            res = param['res']
        
            grid.actions.set_code(cursor, initial_code)
            
            grid.actions.append_reference_code(cursor, ref_key, ref_type)
            
            wx.Yield()
            
            result_code = main_window.entry_line.GetValue()
            
            if "S[" in initial_code:
                assert result_code == initial_code[:4] + res
                
            else:
                assert result_code == initial_code + res
                
    param_set_cell_attr = [ \
        {'selection': Selection([], [], [], [], [(2, 5)]), 'tab': 1,
         'attr': ('bordercolor_right', wx.RED), 'testcell': (2, 5, 1)},
        {'selection': Selection([(0, 0)], [(99, 99)], [], [], []), 'tab': 0,
         'attr': ('bordercolor_right', wx.RED), 'testcell': (2, 5, 0)},
        {'selection': Selection([], [], [], [], [(2, 5)]), 'tab': 1,
         'attr': ('bordercolor_bottom', wx.BLUE), 'testcell': (2, 5, 1)},
        {'selection': Selection([], [], [], [], [(2, 5)]), 'tab': 1,
         'attr': ('bgcolor', wx.RED), 'testcell': (2, 5, 1)},
        {'selection': Selection([], [], [], [], [(2, 5)]), 'tab': 2,
         'attr': ('pointsize', 24), 'testcell': (2, 5, 2)},
    ]
    
    @params(param_set_cell_attr)
    def test_set_cell_attr(self, selection, tab, attr, testcell):
        """Unit test for _set_cell_attr"""
        
        main_window.changed_since_save = False
        
        attr = {attr[0]: attr[1]}
        
        grid.actions._set_cell_attr(selection, tab, attr)
        
        color = grid.code_array.cell_attributes[testcell][attr.keys()[0]]
        
        assert color == attr[attr.keys()[0]]
        
        wx.Yield()
        assert main_window.changed_since_save
    
    def test_set_border_attr(self):
        """Unit test for set_border_attr"""
        
        grid.SelectBlock(10, 10, 20, 20)
        
        attr = "borderwidth"
        value = 5
        borders = ["top", "inner"]
        tests = { \
            (13, 14, 0): 5,
            (53, 14, 0): 1,
        } 
        
        grid.actions.set_border_attr(attr, value, borders)
        
        for cell in tests:
            res = grid.code_array.cell_attributes[cell]["borderwidth_bottom"]
            assert res == tests[cell]
        
    
    def test_toggle_attr(self):
        """Unit test for toggle_attr"""
        
        grid.SelectBlock(10, 10, 20, 20)
        
        grid.actions.toggle_attr("underline")
        
        tests = {(13, 14, 0): True, (53, 14, 0): False}
        
        for cell in tests:
            res = grid.code_array.cell_attributes[cell]["underline"]
            assert res == tests[cell]
    
    def test_change_frozen_attr(self):
        pass
    
    def test_get_new_cell_attr_state(self):
        pass
    
    def test_get_new_selection_attr_state(self):
        pass
    
    def test_refresh_selected_frozen_cells(self):
        pass
        
