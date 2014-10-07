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
_printout.py
============

Printout handling module

"""

import wx
import wx.lib.wxcairo

import src.lib.i18n as i18n

from src.lib._grid_cairo_renderer import GridCairoRenderer

# Use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class Printout(wx.Printout):
    def __init__(self, grid, print_info):

        self.top_row = print_info["top_row"]
        self.bottom_row = print_info["bottom_row"]
        self.left_col = print_info["left_col"]
        self.right_col = print_info["right_col"]
        self.first_tab = print_info["first_tab"]
        self.last_tab = print_info["last_tab"]
        self.width = print_info["paper_width"]
        self.height = print_info["paper_height"]
        self.orientation = print_info["orientation"]

        self.grid = grid

        wx.Printout.__init__(self)

    def HasPage(self, page):
        """Returns True iif page is present"""

        return self.first_tab <= page <= self.last_tab

    def GetPageInfo(self):
        super(Printout, self).GetPageInfo()
        # return (1, 1, 1, 1)

    def OnPrintPage(self, page):
        dc = self.GetDC()

        # ------------------------------------------

        context = wx.lib.wxcairo.ContextFromDC(dc)
        code_array = self.grid.code_array

        # Draw cells
        cell_renderer = GridCairoRenderer(context, code_array,
                                          (self.top_row, self.bottom_row),
                                          (self.left_col, self.right_col),
                                          (page, page + 1),
                                          self.width, self.height,
                                          self.orientation)

        cell_renderer.draw()

        context.show_page()

        dc.EndDrawing()

        return True
