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
xls_import.py
=============

Helper functions for unit tests

"""

def read_xls(filepath):
	"""Inserts xls file content into grid"""

	import xlrd

	workbook = xlrd.open_workbook(filepath)
	for sheet_no, sheet in enumerate(workbook.sheets()):
		for row in xrange(sheet.nrows):
			for col in xrange(sheet.ncols):
				S[row, col, sheet_no] = \
					repr(sheet.cell(row, col).value)

	return filepath
