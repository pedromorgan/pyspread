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

import ast

import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import wx.lib.colourselect as csel

from _widgets import PenWidthComboBox, PenStyleComboBox
from _events import post_command_event, ChartDialogEventMixin
from icons import Icons
import src.lib.i18n as i18n

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class ChartAxisDataPanel(wx.Panel, ChartDialogEventMixin):
    """Panel for data entry for chart axis"""

    def __init__(self, *args, **kwargs):

        self.parent = args[0]
        self.chart_data = kwargs.pop("chart_data")

        wx.Panel.__init__(self, *args, **kwargs)

        self.x_label = wx.StaticText(self, -1, _("X"))
        self.x_text_ctrl = wx.TextCtrl(self, -1, "")
        self.y1_label = wx.StaticText(self, -1, _("Y1"))
        self.y1_text_ctrl = wx.TextCtrl(self, -1, "")
        self.y2_label = wx.StaticText(self, -1, _("Y2"))
        self.y2_text_ctrl = wx.TextCtrl(self, -1, "")

        self.chart_axis_data_staticbox = wx.StaticBox(self, -1, _("Data"))

        self.__set_properties()
        self.__do_layout()
        self.__bindings()

    def __set_properties(self):
        self.x_text_ctrl.SetToolTipString(_("Enter a list of values."))
        self.y1_text_ctrl.SetToolTipString(_("Enter a list of values."))
        self.y2_text_ctrl.SetToolTipString(_("Enter a list of values."))

    def __do_layout(self):
        self.chart_axis_data_staticbox.Lower()
        data_box_sizer = wx.StaticBoxSizer(self.chart_axis_data_staticbox,
                                    wx.HORIZONTAL)
        data_box_grid_sizer = wx.FlexGridSizer(3, 2, 0, 0)

        data_box_grid_sizer.Add(self.x_label, 0, wx.ALL |
                                wx.ALIGN_CENTER_VERTICAL, 2)
        data_box_grid_sizer.Add(self.x_text_ctrl, 0, wx.ALL | wx.EXPAND, 0)
        data_box_grid_sizer.Add(self.y1_label, 0, wx.ALL |
                                wx.ALIGN_CENTER_VERTICAL, 2)
        data_box_grid_sizer.Add(self.y1_text_ctrl, 0, wx.EXPAND, 0)
        data_box_grid_sizer.Add(self.y2_label, 0, wx.ALL |
                                wx.ALIGN_CENTER_VERTICAL, 2)
        data_box_grid_sizer.Add(self.y2_text_ctrl, 0, wx.EXPAND, 0)
        data_box_grid_sizer.AddGrowableCol(1)
        data_box_sizer.Add(data_box_grid_sizer, 1, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(data_box_sizer)

        self.Layout()

    def __bindings(self):
        """Binds events ton handlers"""

        self.Bind(wx.EVT_TEXT, self.OnXText, self.x_text_ctrl)
        self.Bind(wx.EVT_TEXT, self.OnYText, self.y1_text_ctrl)

    # Handlers
    # --------

    def OnXText(self, event):
        """Event handler for x_text_ctrl"""

        self.chart_data["x_data"] = ast.literal_eval(event.GetString())
        post_command_event(self, self.DrawChartMsg)

    def OnYText(self, event):
        """Event handler for y1_text_ctrl"""

        self.chart_data["y1_data"] = ast.literal_eval(event.GetString())
        post_command_event(self, self.DrawChartMsg)


class ChartAxisLinePanel(wx.Panel, ChartDialogEventMixin):
    """"""

    # Handlers
    # --------

    def OnLineWidth(self, event):
        """Line width event handler"""

        self.chart_data["line_width"] = int(event.GetSelection())
        post_command_event(self, self.DrawChartMsg)

    def OnLineColor(self, event):
        """Line color event handler"""

        self.chart_data["line_color"] = \
                tuple(i / 255.0 for i in event.GetValue().Get())
        post_command_event(self, self.DrawChartMsg)


class ChartAxisMarkerPanel(wx.Panel, ChartDialogEventMixin):
    """"""


class ChartDialog(wx.Dialog, ChartDialogEventMixin):
    """Chart dialog for generating chart generation strings"""

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | \
                        wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)

        # Initial data for chart
        self.chart_data = {
            "x_data": [],
            "y1_data": [],
            "y2_data": [],
            "line_width": 1,
            "line_color": (0, 0, 0),
        }

        # Icons for BitmapButtons
        icons = Icons(icon_size=(24, 24))

        self.axis_list_box = wx.ListBox(self, -1, choices=[])
        self.series_staticbox = wx.StaticBox(self, -1, _("Series"))
        self.add_button = wx.BitmapButton(self, -1, icons["Add"])
        self.remove_button = wx.BitmapButton(self, -1, icons["Remove"])
        self.move_up_buttom = wx.BitmapButton(self, -1, icons["GoUp"])
        self.move_down_buttom = wx.BitmapButton(self, -1, icons["GoDown"])
        self.cancel_button = wx.Button(self, wx.ID_CANCEL)
        self.ok_button = wx.Button(self, wx.ID_OK)

        self.chart_axis_data_panel = ChartAxisDataPanel(self, -1,
                                            chart_data=self.chart_data)

        self.label_4 = wx.StaticText(self, -1, _("Style"))
        style_choices = map(unicode, xrange(len(PenStyleComboBox.pen_styles)))
        self.line_style_choice = PenStyleComboBox(self, -1,
                                                  choices=style_choices)
        self.label_5 = wx.StaticText(self, -1, _("Color"))
        self.line_colorselect = csel.ColourSelect(self, -1, unichr(0x2500) * 6,
                                                   size=(80, 25))
        self.label_6 = wx.StaticText(self, -1, _("Width"))
        width_choices = map(unicode, xrange(12))
        self.line_width_combo = PenWidthComboBox(self, choices=width_choices,
                                    style=wx.CB_READONLY, size=(50, -1))
        self.sizer_6_staticbox = wx.StaticBox(self, -1, _("Line"))
        self.label_4_copy = wx.StaticText(self, -1, _("Style"))
        self.marker_style_choice = wx.Choice(self, -1, choices=[])
        self.label_5_copy = wx.StaticText(self, -1, _("Front"))
        self.marker_front_colorselect = csel.ColourSelect(self, -1,
                                                          size=(80, 25))
        self.label_6_copy = wx.StaticText(self, -1, _("Back"))
        self.marker_back_colorselect = csel.ColourSelect(self, -1,
                                                         size=(80, 25))
        self.sizer_7_staticbox = wx.StaticBox(self, -1, _("Marker"))

        self.figure = Figure((5.0, 4.0), facecolor="white")
        self.axes = self.figure.add_subplot(111)
        self.figure_canvas = FigureCanvasWxAgg(self, -1, self.figure)

        self.__set_properties()
        self.__do_layout()
        self.__bindings()

        # Draw figure initially
        post_command_event(self, self.DrawChartMsg)

    def __set_properties(self):
        self.SetTitle(_("Insert chart"))
        self.SetSize((800, 350))
        self.add_button.SetMinSize((24, 24))
        self.add_button.SetToolTipString(_("Add series."))
        self.remove_button.SetMinSize((24, 24))
        self.remove_button.SetToolTipString(_("Remove series."))
        self.move_up_buttom.SetMinSize((24, 24))
        self.move_up_buttom.SetToolTipString(_("Move series up."))
        self.move_down_buttom.SetMinSize((24, 24))
        self.move_down_buttom.SetToolTipString(_("Move series down."))
        self.figure_canvas.SetMinSize((400, 300))

        # Set controls to default values
        self.line_width_combo.SetSelection(self.chart_data["line_width"])

    def __do_layout(self):
        sizer_1 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_4 = wx.FlexGridSizer(1, 1, 0, 0)
        self.sizer_7_staticbox.Lower()
        sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.HORIZONTAL)
        grid_sizer_4_copy = wx.FlexGridSizer(3, 2, 0, 0)
        self.sizer_6_staticbox.Lower()
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        grid_sizer_4 = wx.FlexGridSizer(3, 2, 0, 0)
        sizer_2 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_3 = wx.FlexGridSizer(1, 2, 0, 0)
        grid_sizer_1 = wx.FlexGridSizer(1, 2, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(5, 1, 0, 0)
        grid_sizer_1.Add(self.axis_list_box, 0, wx.EXPAND, 0)
        grid_sizer_2.Add(self.add_button, 0, wx.ALL, 2)
        grid_sizer_2.Add(self.remove_button, 0, wx.ALL, 2)
        grid_sizer_2.Add(self.move_up_buttom, 0, wx.ALL, 2)
        grid_sizer_2.Add(self.move_down_buttom, 0, wx.ALL, 2)
        grid_sizer_2.AddGrowableRow(1)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableCol(0)
        sizer_2.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_3.Add(self.ok_button, 0,
                    wx.ALL | wx.ALIGN_CENTER_HORIZONTAL |
                    wx.ALIGN_CENTER_VERTICAL, 2)
        sizer_3.Add(self.cancel_button, 0,
                    wx.ALL | wx.ALIGN_CENTER_HORIZONTAL |
                    wx.ALIGN_CENTER_VERTICAL, 2)
        sizer_3.AddGrowableRow(0)
        sizer_3.AddGrowableCol(0)
        sizer_3.AddGrowableCol(1)
        sizer_2.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 3)
        sizer_2.AddGrowableRow(0)
        sizer_2.AddGrowableCol(0)
        sizer_series_staticbox = wx.StaticBoxSizer(self.series_staticbox,
                                                   wx.HORIZONTAL)
        sizer_series_staticbox.Add(sizer_2, 1, wx.EXPAND, 0)
        sizer_1.Add(sizer_series_staticbox, 1, wx.EXPAND, 0)
        sizer_4.Add(self.chart_axis_data_panel, 1, wx.ALL | wx.EXPAND, 2)
        grid_sizer_4.Add(self.label_4, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4.Add(self.line_style_choice, 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.label_5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4.Add(self.line_colorselect, 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.label_6, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4.Add(self.line_width_combo, 0, wx.EXPAND, 0)
        grid_sizer_4.AddGrowableCol(1)
        sizer_6.Add(grid_sizer_4, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_6, 1, wx.ALL | wx.EXPAND, 2)
        grid_sizer_4_copy.Add(self.label_4_copy, 0,
                              wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4_copy.Add(self.marker_style_choice, 0, wx.EXPAND, 0)
        grid_sizer_4_copy.Add(self.label_5_copy, 0,
                              wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4_copy.Add(self.marker_front_colorselect, 0, wx.EXPAND, 0)
        grid_sizer_4_copy.Add(self.label_6_copy, 0,
                              wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        grid_sizer_4_copy.Add(self.marker_back_colorselect, 0, wx.EXPAND, 0)
        grid_sizer_4_copy.AddGrowableCol(1)
        sizer_7.Add(grid_sizer_4_copy, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_7, 1, wx.ALL | wx.EXPAND, 2)
        sizer_4.AddGrowableCol(0)
        sizer_series_staticbox.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_1.Add(self.figure_canvas, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)
        self.SetSizer(sizer_1)
        sizer_1.AddGrowableRow(0)
        sizer_1.AddGrowableCol(0)
        self.Layout()

    def __bindings(self):
        """Binds events ton handlers"""

        self.Bind(wx.EVT_COMBOBOX, self.OnLineWidth, self.line_width_combo)
        self.Bind(self.EVT_CMD_DRAW_CHART, self.OnDrawChart)
        self.line_colorselect.Bind(csel.EVT_COLOURSELECT, self.OnLineColor)

    def __disable_controls(self, unneeded_ctrls):
        """Disables the controls that are not needed by chart"""

        for ctrl in unneeded_ctrls:
            ctrl.Disable()

    def draw_chart(self, chart_data):
        """Redraws the chart that is displayed at FigureCanvasWxAgg"""

        # Unpack chart_data

        x_data = chart_data["x_data"]
        y1_data = chart_data["y1_data"]
        line_width = chart_data["line_width"]
        line_color = chart_data["line_color"]

        # Clear the axes and redraw the plot anew

        self.axes.clear()

        if x_data and len(x_data) == len(y1_data):
            self.axes.plot(y1_data, linewidth=line_width, xdata=self.xdata,
                           color=line_color)
        else:
            self.axes.plot(y1_data, linewidth=line_width, color=line_color)

        self.figure_canvas.draw()

    # Handlers
    # --------

    def OnLineWidth(self, event):
        """Line width event handler"""

        self.chart_data["line_width"] = int(event.GetSelection())
        post_command_event(self, self.DrawChartMsg)

    def OnLineColor(self, event):
        """Line color event handler"""

        self.chart_data["line_color"] = \
                tuple(i / 255.0 for i in event.GetValue().Get())
        post_command_event(self, self.DrawChartMsg)

    def OnDrawChart(self, event):
        """Figure drawing event handler"""

        self.draw_chart(self.chart_data)