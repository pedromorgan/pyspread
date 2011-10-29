#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for typechecks.py"""

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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

class TestTypeChecks(object):
    """Unit test for typechecks"""
    
    def setup_method(self, method):
        """Creates empty DataArray"""
        
        self.data_array = DataArray((100, 100, 100))
        
    def test_is_slice_like(self):
        """Test shape attribute"""
        
        assert self.data_array._is_slice_like(slice(None, 4, 34))
        assert not self.data_array._is_slice_like(-2)
        
    def test_is_string_like(self):
        """Test shape attribute"""
        
        assert self.data_array._is_string_like("Test")
        assert not self.data_array._is_string_like(["Test"])
