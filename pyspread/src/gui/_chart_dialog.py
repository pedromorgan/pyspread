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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread. If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_chart_dialog
=============

Chart creation dialog with interactive matplotlib chart widget

Provides
--------

* ChartDialog: Chart dialog class

"""

import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg


class ChartDialog(wx.Dialog):
    """Chart dialog for generating chart generation strings"""

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | \
                        wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)

        self.fig = Figure((5.0, 4.0))

        self.axis_list_box = wx.ListBox(self, -1, choices=[])
        self.button_1 = wx.Button(self, -1, "button_1")
        self.button_2 = wx.Button(self, -1, "button_2")
        self.panel_1 = wx.Panel(self, -1)
        self.button_3 = wx.Button(self, -1, "button_3")
        self.button_4 = wx.Button(self, -1, "button_4")
        self.button_5 = wx.Button(self, -1, "button_5")
        self.button_6 = wx.Button(self, -1, "button_6")
        self.label_1 = wx.StaticText(self, -1, "label_1")
        self.text_ctrl_1 = wx.TextCtrl(self, -1, "")
        self.label_2 = wx.StaticText(self, -1, "label_2")
        self.text_ctrl_2 = wx.TextCtrl(self, -1, "")
        self.label_3 = wx.StaticText(self, -1, "label_3")
        self.text_ctrl_3 = wx.TextCtrl(self, -1, "")
        self.sizer_5_staticbox = wx.StaticBox(self, -1, "Data")
        self.label_4 = wx.StaticText(self, -1, "label_4")
        self.choice_1 = wx.Choice(self, -1, choices=[])
        self.label_5 = wx.StaticText(self, -1, "label_5")
        self.choice_2 = wx.Choice(self, -1, choices=[])
        self.label_6 = wx.StaticText(self, -1, "label_6")
        self.choice_3 = wx.Choice(self, -1, choices=[])
        self.sizer_6_staticbox = wx.StaticBox(self, -1, "Line style")
        self.label_4_copy = wx.StaticText(self, -1, "label_4")
        self.choice_1_copy = wx.Choice(self, -1, choices=[])
        self.label_5_copy = wx.StaticText(self, -1, "label_5")
        self.choice_2_copy = wx.Choice(self, -1, choices=[])
        self.label_6_copy = wx.StaticText(self, -1, "label_6")
        self.choice_3_copy = wx.Choice(self, -1, choices=[])
        self.sizer_7_staticbox = wx.StaticBox(self, -1, "Marker style")
        self.window_1 = FigureCanvasWxAgg(self, -1, self.fig)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle("dialog_1")
        self.SetSize((800, 300))
        self.button_1.SetMinSize((30, 30))
        self.button_2.SetMinSize((30, 30))
        self.button_3.SetMinSize((30, 30))
        self.button_4.SetMinSize((30, 30))
        self.window_1.SetMinSize((400, 300))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_4 = wx.FlexGridSizer(1, 1, 0, 0)
        self.sizer_7_staticbox.Lower()
        sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.HORIZONTAL)
        grid_sizer_4_copy = wx.FlexGridSizer(3, 2, 0, 0)
        self.sizer_6_staticbox.Lower()
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        grid_sizer_4 = wx.FlexGridSizer(3, 2, 0, 0)
        self.sizer_5_staticbox.Lower()
        sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(3, 2, 0, 0)
        sizer_2 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_3 = wx.FlexGridSizer(1, 2, 0, 0)
        grid_sizer_1 = wx.FlexGridSizer(1, 2, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(5, 1, 0, 0)
        grid_sizer_1.Add(self.axis_list_box, 0, wx.EXPAND, 0)
        grid_sizer_2.Add(self.button_1, 0, wx.ALL, 2)
        grid_sizer_2.Add(self.button_2, 0, wx.ALL, 2)
        grid_sizer_2.Add(self.panel_1, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.button_3, 0, wx.ALL, 2)
        grid_sizer_2.Add(self.button_4, 0, wx.ALL, 2)
        grid_sizer_2.AddGrowableRow(2)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableCol(0)
        sizer_2.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_3.Add(self.button_5, 0,
                    wx.ALL | wx.ALIGN_CENTER_HORIZONTAL |
                    wx.ALIGN_CENTER_VERTICAL, 2)
        sizer_3.Add(self.button_6, 0,
                    wx.ALL | wx.ALIGN_CENTER_HORIZONTAL |
                    wx.ALIGN_CENTER_VERTICAL, 2)
        sizer_3.AddGrowableRow(0)
        sizer_3.AddGrowableCol(0)
        sizer_3.AddGrowableCol(1)
        sizer_2.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 3)
        sizer_2.AddGrowableRow(0)
        sizer_2.AddGrowableCol(0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_3.Add(self.label_1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_3.Add(self.text_ctrl_1, 0, wx.ALL | wx.EXPAND, 0)
        grid_sizer_3.Add(self.label_2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_3.Add(self.text_ctrl_2, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.label_3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_3.Add(self.text_ctrl_3, 0, wx.EXPAND, 0)
        grid_sizer_3.AddGrowableCol(1)
        sizer_5.Add(grid_sizer_3, 1, wx.ALL | wx.EXPAND, 2)
        sizer_4.Add(sizer_5, 1, wx.ALL | wx.EXPAND, 2)
        grid_sizer_4.Add(self.label_4, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4.Add(self.choice_1, 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.label_5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4.Add(self.choice_2, 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.label_6, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4.Add(self.choice_3, 0, wx.EXPAND, 0)
        grid_sizer_4.AddGrowableCol(1)
        sizer_6.Add(grid_sizer_4, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_6, 1, wx.ALL | wx.EXPAND, 2)
        grid_sizer_4_copy.Add(self.label_4_copy, 0,
                              wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4_copy.Add(self.choice_1_copy, 0, wx.EXPAND, 0)
        grid_sizer_4_copy.Add(self.label_5_copy, 0,
                              wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4_copy.Add(self.choice_2_copy, 0, wx.EXPAND, 0)
        grid_sizer_4_copy.Add(self.label_6_copy, 0,
                              wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4_copy.Add(self.choice_3_copy, 0, wx.EXPAND, 0)
        grid_sizer_4_copy.AddGrowableCol(1)
        sizer_7.Add(grid_sizer_4_copy, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_7, 1, wx.ALL | wx.EXPAND, 2)
        sizer_4.AddGrowableCol(0)
        sizer_1.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_1.Add(self.window_1, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)
        self.SetSizer(sizer_1)
        sizer_1.AddGrowableRow(0)
        sizer_1.AddGrowableCol(0)
        self.Layout()
        # end wxGlade

# end of class MyDialog
if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    dialog_1 = ChartDialog(None, -1, "")
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()