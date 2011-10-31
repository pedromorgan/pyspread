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

from lib.testlib import main_window, grid, code_array
from lib.testlib import params, pytest_generate_tests
from lib.testlib import basic_setup_test, restore_basic_grid

class TestCellActions(object):
    """Cell actions test class"""
    
    def test_set_code(self):
        pass
    
    def test_delete_cell(self):
        pass
    
    def test_get_absolute_reference(self):
        pass
    
    def test_get_relative_reference(self):
        pass
    
    def test_append_reference_code(self):
        pass
    
    def test_set_cell_attr(self):
        pass
    
    def test_set_attr(self):
        pass
    
    def test_set_border_attr(self):
        pass
    
    def test_toggle_attr(self):
        pass
    
    def test_change_frozen_attr(self):
        pass
    
    def test_get_new_cell_attr_state(self):
        pass
    
    def test_get_new_selection_attr_state(self):
        pass
    
    def test_refresh_selected_frozen_cells(self):
        pass
        
