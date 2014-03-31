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

from copy import copy
from datetime import datetime
from itertools import product

try:
    import xlrd

except ImportError:
    xlrd = None

try:
    import xlwt

except ImportError:
    xlwt = None

import wx

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

        self.xls_max_rows = 65536
        self.xls_max_cols = 256
        self.xls_max_tabs = 256  # Limit tables to 255 to avoid cluttered Excel

    def idx2colour(self, idx):
        """Returns wx.Colour"""

        return wx.Colour(*self.workbook.colour_map[idx])

    def color2idx(self, red, green, blue):
        """Get an Excel index from"""

        xlwt_colors = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255), (0, 0, 0),
            (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 0, 0),
            (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128),
            (0, 128, 128), (192, 192, 192), (128, 128, 128), (153, 153, 255),
            (153, 51, 102), (255, 255, 204), (204, 255, 255), (102, 0, 102),
            (255, 128, 128), (0, 102, 204), (204, 204, 255), (0, 0, 128),
            (255, 0, 255), (255, 255, 0), (0, 255, 255), (128, 0, 128),
            (128, 0, 0), (0, 128, 128), (0, 0, 255), (0, 204, 255),
            (204, 255, 255), (204, 255, 204), (255, 255, 153), (153, 204, 255),
            (255, 153, 204), (204, 153, 255), (255, 204, 153), (51, 102, 255),
            (51, 204, 204), (153, 204, 0), (255, 204, 0), (255, 153, 0),
            (255, 102, 0), (102, 102, 153), (150, 150, 150), (0, 51, 102),
            (51, 153, 102), (0, 51, 0), (51, 51, 0), (153, 51, 0),
            (153, 51, 102), (51, 51, 153), (51, 51, 51)
        ]

        distances = [abs(red - r) + abs(green - g) + abs(blue - b)
                     for r, g, b in xlwt_colors]

        min_dist_idx = distances.index(min(distances))

        return min_dist_idx

    def _shape2xls(self, worksheets):
        """Writes shape to xls file

        Format: <rows>\t<cols>\t<tabs>\n

        """

        __, __, tabs = self.code_array.shape

        if tabs > self.xls_max_tabs:
            tabs = self.xls_max_tabs

        for tab in xrange(tabs):
            worksheet = self.workbook.add_sheet(str(tab))
            worksheets.append(worksheet)

    def _xls2shape(self):
        """Updates shape in code_array"""

        sheets = self.workbook.sheets()
        nrows = sheets[0].nrows
        ncols = sheets[0].ncols
        ntabs = len(sheets)

        self.code_array.shape = nrows, ncols, ntabs

    def _code2xls(self, worksheets):
        """Writes code to xls file

        Format: <row>\t<col>\t<tab>\t<code>\n

        """

        xls_max_shape = self.xls_max_rows, self.xls_max_cols, self.xls_max_tabs

        for key in self.code_array:
            if all(kele < mele for kele, mele in zip(key, xls_max_shape)):
                # Cell lies within Excel boundaries
                row, col, tab = key
                code_str = self.code_array(key)
                style = self._get_xfstyle(worksheets, key)
                worksheets[tab].write(row, col, label=code_str, style=style)

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

    def _get_xfstyle(self, worksheets, key):
        """Gets XFStyle for cell key"""

        dict_grid = self.code_array.dict_grid

        # Get all cells in selections

        pys_style = dict_grid.cell_attributes[key]
        xfstyle = xlwt.XFStyle()

        # Font
        # ----

        if "textfont" in pys_style:

            font = xlwt.Font()

            font.name = pys_style["textfont"]

            if "pointsize" in pys_style:
                font.height = pys_style["pointsize"] * 20.0

            if "fontweight" in pys_style:
                font.bold = (pys_style["fontweight"] == wx.BOLD)

            if "fontstyle" in pys_style:
                font.italic = (pys_style["fontstyle"] == wx.ITALIC)

            if "textcolor" in pys_style:
                textcolor = wx.Colour()
                textcolor.SetRGB(pys_style["textcolor"])
                font.colour_index = self.color2idx(*textcolor.Get())

            if "underline" in pys_style:
                font.underline_type = pys_style["underline"]

            if "strikethrough" in pys_style:
                font.struck_out = pys_style["strikethrough"]

            xfstyle.font = font

        # Alignment
        # ---------

        if any(e in pys_style for e in ["justification", "vertical_align",
                                        "angle"]):
            alignment = xlwt.Alignment()

        if "justification" in pys_style:
            justification2xfalign = {
                "left": 1,
                "center": 2,
                "right": 3,
            }

            alignment.horz = justification2xfalign[pys_style["justification"]]

        if "vertical_align" in pys_style:
            vertical_align2xfalign = {
                "top": 0,
                "middle": 1,
                "bottom": 2,
            }

            alignment.vert = \
                vertical_align2xfalign[pys_style["vertical_align"]]

        if "angle" in pys_style:
            def angle2xfrotation(angle):
                """Returns angle from xlrotatation"""

                # angle is counterclockwise
                if 0 <= angle <= 90:
                    return angle

                elif -90 <= angle < 0:
                    return 90 - angle

                return 0

            alignment.rota = angle2xfrotation(pys_style["angle"])

        if any(e in pys_style for e in ["justification", "vertical_align",
                                        "angle"]):
            xfstyle.alignment = alignment

        # Background
        # ----------

        if "bgcolor" in pys_style:
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN

            bgcolor = wx.Colour()
            bgcolor.SetRGB(pys_style["bgcolor"])
            pattern.pattern_fore_colour = self.color2idx(*bgcolor.Get())

            xfstyle.pattern = pattern

        # Border
        # ------

#        width2border_line_style = {
#            1: 0,
#            1: 1,
#            2: 1,
#            3: 1,
#            4: 1,
#            5: 2,
#            6: 2,
#            7: 5,
#            8: 5,
#            9: 5,
#        }
#
#        border_keys = [
#            "borderwidth_right",
#            "borderwidth_bottom",
#            "bordercolor_right"
#            "bordercolor_bottom"
#        ]
#
#        if any(border_key in pys_style for border_key in border_keys):
#            border = xlwt.Borders()
#
#        try:
#            border_pys_style = pys_style["borderwidth_right"]
#            border_line_style = width2border_line_style[border_pys_style]
#            border.right_line_style = border_line_style
#
#        except KeyError:
#            # No or unknown border width
#            pass
#
#        try:
#            border_pys_style = pys_style["borderwidth_bottom"]
#            border_line_style = width2border_line_style[border_pys_style]
#            border.bottom_line_style = border_line_style
#
#        except KeyError:
#            # No or unknown border width
#            pass
#
#        try:
#            print pys_style["bordercolor_right"]
#            border_pys_style = pys_style["bordercolor_right"]
#            bcolor = wx.Colour()
#            bcolor.SetRGB(border_pys_style)
#            border.right_colour_index = self.color2idx(*bgcolor.Get())
#            print bcolor, border.right_colour_index
#
#        except KeyError:
#            # No or unknown border color
#            pass
#
#        try:
#            border_pys_style = pys_style["bordercolor_bottom"]
#            bcolor = wx.Colour()
#            bcolor.SetRGB(border_pys_style)
#            border.bottom_colour_index = self.color2idx(*bgcolor.Get())
#
#        except KeyError:
#            # No or unknown border color
#            pass
#
#        if any(border_key in pys_style for border_key in border_keys):
#            xfstyle.border = border

        return xfstyle

    def _xls2attributes(self, worksheet, tab):
        """Updates attributes in code_array"""

        # Merged cells
        for top, bottom, left, right in worksheet.merged_cells:
            attrs = {"merge_area": (top, left, bottom - 1, right - 1)}
            selection = Selection([(top, left)], [(bottom - 1, right - 1)],
                                  [], [], [])
            self.code_array.cell_attributes.append((selection, tab, attrs))

        # Which cell comprise which format ids
        xf2cell = dict((xfid, []) for xfid in xrange(self.workbook.xfcount))
        rows, cols = worksheet.nrows, worksheet.ncols
        for row, col in product(xrange(rows), xrange(cols)):
            xfid = worksheet.cell_xf_index(row, col)
            xf2cell[xfid].append((row, col))

        for xfid, xf in enumerate(self.workbook.xf_list):
            selection = Selection([], [], [], [], xf2cell[xfid])
            selection_above = selection.shifted(-1, 0)
            selection_left = selection.shifted(0, -1)

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
            if xf.background.fill_pattern == 1:
                color_idx = xf.background.pattern_colour_index
                color = self.idx2colour(color_idx)
                attributes["bgcolor"] = color.GetRGB()

            # Border
            border_line_style2width = {
                0: 1,
                1: 3,
                2: 5,
                5: 7,
            }

            bottom_color_idx = xf.border.bottom_colour_index
            if self.workbook.colour_map[bottom_color_idx] is not None:
                bottom_color = self.idx2colour(bottom_color_idx)
                attributes["bordercolor_bottom"] = bottom_color.GetRGB()

            right_color_idx = xf.border.right_colour_index
            if self.workbook.colour_map[right_color_idx] is not None:
                right_color = self.idx2colour(right_color_idx)
                attributes["bordercolor_right"] = right_color.GetRGB()

            bottom_width = border_line_style2width[xf.border.bottom_line_style]
            attributes["borderwidth_bottom"] = bottom_width

            right_width = border_line_style2width[xf.border.right_line_style]
            attributes["borderwidth_right"] = right_width

            # Font

            font = self.workbook.font_list[xf.font_index]

            attributes["textfont"] = font.name
            attributes["pointsize"] = font.height / 20.0

            fontweight = wx.BOLD if font.weight == 700 else wx.NORMAL
            attributes["fontweight"] = fontweight

            if font.italic:
                attributes["fontstyle"] = wx.ITALIC

            if self.workbook.colour_map[font.colour_index] is not None:
                attributes["textcolor"] = \
                    self.idx2colour(font.colour_index).GetRGB()

            if font.underline_type:
                attributes["underline"] = True

            if font.struck_out:
                attributes["strikethrough"] = True

            # Handle cells above for top borders

            attributes_above = {}
            top_width = border_line_style2width[xf.border.top_line_style]
            if top_width != 1:
                attributes_above["borderwidth_bottom"] = top_width
            top_color_idx = xf.border.top_colour_index
            if self.workbook.colour_map[top_color_idx] is not None:
                top_color = self.idx2colour(top_color_idx)
                attributes_above["bordercolor_bottom"] = top_color.GetRGB()

            # Handle cells above for left borders

            attributes_left = {}
            left_width = border_line_style2width[xf.border.left_line_style]
            if left_width != 1:
                attributes_left["borderwidth_right"] = left_width
            left_color_idx = xf.border.left_colour_index
            if self.workbook.colour_map[left_color_idx] is not None:
                left_color = self.idx2colour(left_color_idx)
                attributes_above["bordercolor_right"] = left_color.GetRGB()

            if attributes_above:
                self._cell_attribute_append(selection_above, tab,
                                            attributes_above)
            if attributes_left:
                self._cell_attribute_append(selection_left, tab,
                                            attributes_left)
            if attributes:
                self._cell_attribute_append(selection, tab, attributes)

    def _cell_attribute_append(self, selection, tab, attributes):
        """Appends to cell_attributes with checks"""

        cell_attributes = self.code_array.cell_attributes

        thick_bottom_cells = []
        thick_right_cells = []

        # Does any cell in selection.cells have a larger bottom border?

        if "borderwidth_bottom" in attributes:
            bwidth = attributes["borderwidth_bottom"]
            for row, col in selection.cells:
                __bwidth = cell_attributes[row, col, tab]["borderwidth_bottom"]
                if __bwidth > bwidth:
                    thick_bottom_cells.append((row, col))

        # Does any cell in selection.cells have a larger right border?
        if "borderwidth_right" in attributes:
            rwidth = attributes["borderwidth_right"]
            for row, col in selection.cells:
                __rwidth = cell_attributes[row, col, tab]["borderwidth_right"]
                if __rwidth > rwidth:
                    thick_right_cells.append((row, col))

        for thick_cell in thick_bottom_cells + thick_right_cells:
            selection.cells.pop(selection.cells.index(thick_cell))

        cell_attributes.append((selection, tab, attributes))

        if thick_bottom_cells:
            bsel = copy(selection)
            bsel.cells = thick_bottom_cells
            battrs = copy(attributes)
            battrs.pop("borderwidth_bottom")
            cell_attributes.append((bsel, tab, battrs))

        if thick_right_cells:
            rsel = copy(selection)
            rsel.cells = thick_right_cells
            rattrs = copy(attributes)
            rattrs.pop("borderwidth_right")
            cell_attributes.append((bsel, tab, battrs))

    def _row_heights2xls(self, worksheets):
        """Writes row_heights to xls file

        Format: <row>\t<tab>\t<value>\n

        """

        xls_max_rows, xls_max_tabs = self.xls_max_rows, self.xls_max_tabs

        dict_grid = self.code_array.dict_grid

        for row, tab in dict_grid.row_heights:
            if row < xls_max_rows and tab < xls_max_tabs:
                height_pixels = dict_grid.row_heights[(row, tab)]
                height_inches = height_pixels / float(get_dpi()[1])
                height_points = height_inches * 72.0

                worksheets[tab].row(row).height_mismatch = True
                worksheets[tab].row(row).height = int(height_points * 20.0)

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

    def _col_widths2xls(self, worksheets):
        """Writes col_widths to xls file

        Format: <col>\t<tab>\t<value>\n

        """

        xls_max_cols, xls_max_tabs = self.xls_max_cols, self.xls_max_tabs

        dict_grid = self.code_array.dict_grid

        for col, tab in dict_grid.col_widths:
            if col < xls_max_cols and tab < xls_max_tabs:
                width_0 = get_default_text_extent("0")[0]
                width_pixels = dict_grid.col_widths[(col, tab)]
                width_0_char = width_pixels * 1.2 / width_0

                worksheets[tab].col(col).width_mismatch = True
                worksheets[tab].col(col).width = int(width_0_char * 256.0)

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
        """Returns xls workbook object with everything from code_array"""

        worksheets = []
        self._shape2xls(worksheets)

        self._code2xls(worksheets)

        self._row_heights2xls(worksheets)
        self._col_widths2xls(worksheets)

        return self.workbook

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
