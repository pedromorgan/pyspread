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
_chart_dialog
=============

Provides
--------
 1. LineChartDialog: Matplotlib line chart configuration dialog

"""

import wx

import src.lib.i18n as i18n

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class AxisDataPanel(wx.Panel):
    """Panel for entering data sets for one axis

    Parameters
    ----------
    no_initial_datasets: Integer, defaults to 1
    \tInitial number of datasets in panel
    no_max_datasets: Integer, defaults to None
    \tMaximum number of datasets for panel

    """

    def __init__(self, *args, **kwargs):
        try:
            self.no_initial_datasets = kwargs.pop("no_initial_datasets")
        except KeyError:
            self.no_initial_datasets = 1

        try:
            self.no_max_datasets = kwargs.pop("no_max_datasets")
        except KeyError:
            self.no_max_datasets = None

        assert self.no_max_datasets is None or \
               self.no_max_datasets >= self.no_initial_datasets

        wx.Panel.__init__(self, *args, **kwargs)

        self.main_grid_sizer = wx.FlexGridSizer(1, 3, 0, 0)

        self.labels = []
        self.textctrls = []

        for setnumber in xrange(self.no_initial_datasets):
            self.add_dataset()

        self.__do_layout()

    def __do_layout(self):
        """Sizer hell"""

        self.SetSizer(self.main_grid_sizer)
        self.main_grid_sizer.Fit(self)
        self.main_grid_sizer.AddGrowableRow(1)
        self.main_grid_sizer.AddGrowableCol(0)
        self.Layout()

    def add_dataset(self):
        """Adds one dataset mask to the panel"""

        label = wx.StaticText(self, -1, "label")
        textctrl = wx.TextCtrl(self)

        self.labels.append(label)
        self.textctrls.append(textctrl)

        self.main_grid_sizer.Add(label)
        self.main_grid_sizer.Add(textctrl)

        self.Layout()

    def pop_dataset(self):
        """Removes one dataset mask from the panel"""

        label = self.labels.pop(-1)
        textctrl = self.textctrls.pop(-1)

        raise NotImplementedError


class ChartDialog(wx.Dialog):
    """Matplotlib chart configuration dialog

    Parameters:
    -----------
    figure: matplotlib.figure
    \tFigure that initialized the dialog content

    """
    def __init__(self, *args, **kwargs):
        self.figure = kwargs.pop("figure")

        kwargs["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwargs)

        self.label_1 = wx.StaticText(self, -1, "label_1")
        self.text_ctrl_1 = wx.TextCtrl(self, -1, "")
        self.label_2 = wx.StaticText(self, -1, "label_2")
        self.text_ctrl_2 = wx.TextCtrl(self, -1, "")
        self.label_3 = wx.StaticText(self, -1, "label_3")
        self.text_ctrl_3 = wx.TextCtrl(self, -1, "")
        self.label_4 = wx.StaticText(self, -1, "label_4")
        self.text_ctrl_4 = wx.TextCtrl(self, -1, "")
        self.static_line_1 = wx.StaticLine(self, -1)
        self.static_line_2 = wx.StaticLine(self, -1)
        self.label_5 = wx.StaticText(self, -1, "label_5")
        self.text_ctrl_5 = wx.TextCtrl(self, -1, "")
        self.sizer_2_staticbox = wx.StaticBox(self, -1, "Data series")
        self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_3D | wx.SP_BORDER)
        self.window_1_pane_1 = AxisDataPanel(self.window_1, -1)
        self.label_6 = wx.StaticText(self.window_1_pane_1, -1, "label_6")
        self.choice_1 = wx.Choice(self.window_1_pane_1, -1, choices=[])
        self.label_7 = wx.StaticText(self.window_1_pane_1, -1, "label_7")
        self.choice_2 = wx.Choice(self.window_1_pane_1, -1, choices=[])
        self.window_1_pane_2 = wx.Panel(self.window_1, -1)
        self.button_1 = wx.Button(self, -1, "button_1")
        self.button_2 = wx.Button(self, -1, "button_2")
        self.button_3 = wx.Button(self, -1, "button_3")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: ChartDialog.__set_properties
        self.SetTitle("dialog_1")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ChartDialog.__do_layout
        sizer_1 = wx.FlexGridSizer(3, 1, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(1, 3, 0, 0)
        grid_sizer_3 = wx.FlexGridSizer(2, 2, 0, 0)
        self.sizer_2_staticbox.Lower()
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(6, 2, 3, 3)
        grid_sizer_1.Add(self.label_1, 0, 0, 0)
        grid_sizer_1.Add(self.text_ctrl_1, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.label_2, 0, 0, 0)
        grid_sizer_1.Add(self.text_ctrl_2, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.label_3, 0, 0, 0)
        grid_sizer_1.Add(self.text_ctrl_3, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.label_4, 0, 0, 0)
        grid_sizer_1.Add(self.text_ctrl_4, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.static_line_1, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 2)
        grid_sizer_1.Add(self.static_line_2, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 2)
        grid_sizer_1.Add(self.label_5, 0, 0, 0)
        grid_sizer_1.Add(self.text_ctrl_5, 0, wx.EXPAND, 0)
        grid_sizer_1.AddGrowableCol(1)
        sizer_2.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_3.Add(self.label_6, 0, 0, 0)
        grid_sizer_3.Add(self.choice_1, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.label_7, 0, 0, 0)
        grid_sizer_3.Add(self.choice_2, 0, wx.EXPAND, 0)
        self.window_1_pane_1.SetSizer(grid_sizer_3)
        grid_sizer_3.AddGrowableCol(1)
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2)
        sizer_1.Add(self.window_1, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.button_1, 0, 0, 0)
        grid_sizer_2.Add(self.button_2, 0, 0, 0)
        grid_sizer_2.Add(self.button_3, 0, 0, 0)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_2.AddGrowableCol(1)
        grid_sizer_2.AddGrowableCol(2)
        sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.AddGrowableRow(1)
        sizer_1.AddGrowableCol(0)
        self.Layout()
