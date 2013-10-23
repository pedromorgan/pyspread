#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# xlspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xlspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xlspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

xls
===

This file contains interfaces to Excel xls file format.

"""

from datetime import datetime
from itertools import product

import xlrd

import src.lib.i18n as i18n

from src.lib.selection import Selection

from src.sysvars import get_dpi, get_default_text_extent


#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class Xls(object):
    """Interface between code_array and xls file

    The xls file is read from disk with the read method.
    The xls file is written to disk with the write method.

    Parameters
    ----------

    code_array: model.CodeArray object
    \tThe code_array object data structure
    workbook: xlrd Workbook object
    \tFile like object in xls format

    """

    def __init__(self, code_array, workbook):
        self.code_array = code_array
        self.workbook = workbook

    def _shape2xls(self):
        """Writes shape to xls file

        Format: <rows>\t<cols>\t<tabs>\n

        """

#        shape_line = u"\t".join(map(unicode, self.code_array.shape)) + u"\n"
#        self.xls_file.write(shape_line)

    def _xls2shape(self):
        """Updates shape in code_array"""

        sheets = self.workbook.sheets()
        nrows = sheets[0].nrows
        ncols = sheets[0].ncols
        ntabs = len(sheets)

        self.code_array.shape = nrows, ncols, ntabs

    def _code2xls(self):
        """Writes code to xls file

        Format: <row>\t<col>\t<tab>\t<code>\n

        """

#        for key in self.code_array:
#            key_str = u"\t".join(repr(ele) for ele in key)
#            code_str = self.code_array(key)
#            out_str = key_str + u"\t" + code_str + u"\n"
#
#            self.xls_file.write(out_str.encode("utf-8"))

    def _xls2code(self, worksheet, tab):
        """Updates code in xls code_array"""

        type2mapper = {
            0: lambda x: None,  # Empty cell
            1: lambda x: repr(x),  # Text cell
            2: lambda x: repr(x),  # Number cell
            3: lambda x: repr(datetime(
                xlrd.xldate_as_tuple(x, self.workbook.datemode))),  # Date
            4: lambda x: repr(bool(x)),  # Boolean cell
            5: lambda x: repr(x),  # Error cell
            6: lambda x: None,  # Blank cell
        }

        rows, cols = worksheet.nrows, worksheet.ncols
        for row, col in product(xrange(rows), xrange(cols)):
            cell_type = worksheet.cell_type(row, col)
            cell_value = worksheet.cell_value(row, col)

            key = row, col, tab
            self.code_array[key] = type2mapper[cell_type](cell_value)

    def _attributes2xls(self):
        """Writes attributes to xls file

        Format:
        <selection[0]>\t[...]\t<tab>\t<key>\t<value>\t[...]\n

        """

#        for selection, tab, attr_dict in self.code_array.cell_attributes:
#            sel_list = [selection.block_tl, selection.block_br,
#                        selection.rows, selection.cols, selection.cells]
#
#            tab_list = [tab]
#
#            attr_dict_list = []
#            for key in attr_dict:
#                attr_dict_list.append(key)
#                attr_dict_list.append(attr_dict[key])
#
#            line_list = map(repr, sel_list + tab_list + attr_dict_list)
#
#            self.xls_file.write(u"\t".join(line_list) + u"\n")

    def _xls2attributes(self, worksheet, tab):
        """Updates attributes in code_array"""

        # Merged cells
        for top, bottom, left, right in worksheet.merged_cells:
            attrs = {"merge_area": (top, left, bottom, right)}
            selection = Selection([(top, left)], [(bottom, right)], [], [], [])
            self.code_array.cell_attributes.append((selection, tab, attrs))

        # Which cell comprise which format ids
        xf2cell = dict((xfid, []) for xfid in xrange(self.workbook.xfcount))
        rows, cols = worksheet.nrows, worksheet.ncols
        for row, col in product(xrange(rows), xrange(cols)):
            xfid = worksheet.cell_xf_index(row, col)
            xf2cell[xfid].append((row, col))

        # Make selection from cells
        xf2selection = {}
        for xfid in xf2cell:
            selection = Selection([], [], [], [], xf2cell[xfid])
            xf2selection[xfid] = selection

        for xfid, xf in enumerate(self.workbook.xf_list):
            attributes = {}

            # Alignment

            xfalign2justification = {
                0: "left",
                1: "left",
                2: "center",
                3: "right",
                4: "left",
                5: "left",
                6: "center",
                7: "left",
            }

            xfalign2vertical_align = {
                0: "top",
                1: "middle",
                2: "bottom",
                3: "middle",
                4: "middle",
            }

            def xfrotation2angle(xfrotation):
                """Returns angle from xlrotatation"""

                # angle is counterclockwise
                if 0 <= xfrotation <= 90:
                    return xfrotation

                elif 90 < xfrotation <= 180:
                    return - (xfrotation - 90)

                return 0

            try:
                attributes["justification"] = \
                    xfalign2justification[xf.alignment.hor_align]

                attributes["vertical_align"] = \
                    xfalign2vertical_align[xf.alignment.vert_align]

                attributes["angle"] = \
                    xfrotation2angle(xf.alignment.rotation)

            except AttributeError:
                pass

            # Background

            # Border

            # Font

            self.code_array.cell_attributes.append(
                (xf2selection[xfid], tab, attributes))

    def _row_heights2xls(self):
        """Writes row_heights to xls file

        Format: <row>\t<tab>\t<value>\n

        """

#        for row, tab in self.code_array.dict_grid.row_heights:
#            height = self.code_array.dict_grid.row_heights[(row, tab)]
#            height_strings = map(repr, [row, tab, height])
#            self.xls_file.write(u"\t".join(height_strings) + u"\n")

    def _xls2row_heights(self, worksheet, tab):
        """Updates row_heights in code_array"""

        for row in xrange(worksheet.nrows):
            try:
                height_points = worksheet.rowinfo_map[row].height / 20.0
                height_inches = height_points / 72.0
                height_pixels = height_inches * get_dpi()[1]

                self.code_array.row_heights[row, tab] = height_pixels

            except KeyError:
                pass

    def _col_widths2xls(self):
        """Writes col_widths to xls file

        Format: <col>\t<tab>\t<value>\n

        """

#        for col, tab in self.code_array.dict_grid.col_widths:
#            width = self.code_array.dict_grid.col_widths[(col, tab)]
#            width_strings = map(repr, [col, tab, width])
#            self.xls_file.write(u"\t".join(width_strings) + u"\n")

    def _xls2col_widths(self, worksheet, tab):
        """Updates col_widths in code_array"""

        for col in xrange(worksheet.ncols):
            try:
                width_0_char = worksheet.colinfo_map[col].width / 256.0
                width_0 = get_default_text_extent("0")[0]
                # Scale relative to 10 point font instead of 12 point
                width_pixels = width_0_char * width_0 / 1.2

                self.code_array.col_widths[col, tab] = width_pixels

            except KeyError:
                pass

    # Access via model.py data
    # ------------------------

    def from_code_array(self):
        """Replaces everything in xls_file from code_array"""

    def to_code_array(self):
        """Replaces everything in code_array from xls_file"""

        self._xls2shape()

        worksheets = self.workbook.sheet_names()

        for tab, worksheet_name in enumerate(worksheets):
            worksheet = self.workbook.sheet_by_name(worksheet_name)
            self._xls2code(worksheet, tab)
            self._xls2attributes(worksheet, tab)
            self._xls2row_heights(worksheet, tab)
            self._xls2col_widths(worksheet, tab)
