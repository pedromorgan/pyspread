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
        # Initial datasets are created immediately
        # Non-initial datasets have to be unveiled by calling add_dataset

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

        self.plus_button = wx.Button(self, -1, label="+")
        self.minus_button = wx.Button(self, -1, label="-")

        self.labels = []
        self.textctrls = []

        self._bind()
        self.__do_layout()

    def _bind(self):
        """Bind events to handlers"""

        self.Bind(wx.EVT_BUTTON, self.OnPlus, self.plus_button)
        self.Bind(wx.EVT_BUTTON, self.OnMinus, self.minus_button)

    def __do_layout(self):
        """Initial layout"""

        self.sizer = wx.FlexGridSizer(1, 2, 0, 0)
        self.datasizer = wx.FlexGridSizer(1, 2, 0, 0)
        buttonsizer = wx.FlexGridSizer(2, 1, 0, 0)

        for setnumber in xrange(self.no_initial_datasets):
            self.add_dataset()

        self.sizer.Add(self.datasizer)
        self.sizer.Add(buttonsizer)

        buttonsizer.Add(self.plus_button)
        buttonsizer.Add(self.minus_button)

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.sizer.AddGrowableRow(1)
        self.sizer.AddGrowableCol(0)

        self.Layout()

    def add_dataset(self):
        """Adds one dataset mask to the panel"""

        label = wx.StaticText(self, -1, "label")
        textctrl = wx.TextCtrl(self)

        self.labels.append(label)
        self.textctrls.append(textctrl)

        self.datasizer.Add(label)
        self.datasizer.Add(textctrl)

        self.Layout()

    def pop_dataset(self):
        """Removes one dataset mask from the panel"""

        if len(self.labels) < 1:
            return

        label = self.labels.pop(-1)
        textctrl = self.textctrls.pop(-1)

        label.Destroy()
        textctrl.Destroy()

        if len(self.labels) <= 1:
            self.minus_button.Disable()

        self.Layout()

    # Event handlers

    def OnPlus(self, event):
        """Handler for plus button"""

        self.add_dataset()
        self.minus_button.Enable(True)

    def OnMinus(self, event):
        """Handler for minus button"""

        self.pop_dataset()


class ChartDataPanel(wx.Panel):
    """Panel for entering all chart data

    Parameters
    ----------
    axes: Iterable of string
    \tLabels of axes
    maxseries: Iterable of Integer
    \tMaximum number of series per axis must equal axes in length

    """

    def __init__(self, *args, **kwargs):
        parent = args[0]
        self.axes = list(kwargs.pop("axes"))
        self.maxseries = list(kwargs.pop("maxseries"))

        assert len(self.axes) == len(self.maxseries)

        wx.Panel.__init__(self, *args, **kwargs)

        self.axis_data_panels = []

        for axis, maxseries in zip(self.axes, self.maxseries):
            axis_data_panel = AxisDataPanel(parent, -1,
                                            no_max_datasets=maxseries)
            self.axis_data_panels.append(axis_data_panel)
        self.__do_layout()

    def __do_layout(self):
        sizer = wx.FlexGridSizer(len(self.axis_data_panels), 1, 0, 0)

        for item in self.axis_data_panels:
            sizer.Add(item)

        self.SetSizer(sizer)
        sizer.Fit(self)
        sizer.AddGrowableCol(0)
        self.Layout()


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

        axes = ["x", "y"]
        maxseries = [1, 3]

        self.chart_data_panel = ChartDataPanel(self, axes=axes,
                                               maxseries=maxseries)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle(_("Insert chart"))

    def __do_layout(self):
        # begin wxGlade: ChartDialog.__do_layout
        sizer = wx.FlexGridSizer(3, 1, 0, 0)
        sizer.Add(self.chart_data_panel, 1, wx.EXPAND, 0)

        self.SetSizer(sizer)
        sizer.Fit(self)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(0)

        self.Layout()