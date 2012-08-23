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


class BoxedPanel(wx.Panel, ChartDialogEventMixin):
    """Base class for boxed panels with labeled widgets"""

    def __init__(self, *args, **kwargs):

        self.parent = args[0]
        self.chart_data = kwargs.pop("chart_data")

        box_label = kwargs.pop("box_label")
        self.widgets = kwargs.pop("widgets")

        wx.Panel.__init__(self, *args, **kwargs)

        self.staticbox = wx.StaticBox(self, -1, box_label)

        for name, label, widget_cls, args, kwargs in self.widgets:
            widget = widget_cls(*args, **kwargs)

            label_name = name + "_label"
            editor_name = name + "_editor"

            setattr(self, label_name, wx.StaticText(self, -1, label))
            setattr(self, editor_name, widget)

        self.__do_layout()

    def __do_layout(self):
        self.staticbox.Lower()
        box_sizer = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        box_grid_sizer = wx.FlexGridSizer(3, 2, 0, 0)

        for name, label, widget_cls, args, kwargs in self.widgets:
            label_name = name + "_label"
            editor_name = name + "_editor"

            label = getattr(self, label_name)
            editor = getattr(self, editor_name)

            box_grid_sizer.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
            box_grid_sizer.Add(editor, 0, wx.ALL | wx.EXPAND, 0)

        box_grid_sizer.AddGrowableCol(1)
        box_sizer.Add(box_grid_sizer, 1, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(box_sizer)

        self.Layout()


class ChartAxisDataPanel(BoxedPanel):
    """Panel for data entry for chart axis"""

    def __init__(self, *args, **kwargs):

        # Custom data
        kwargs["box_label"] = _("Data")

        kwargs["widgets"] = [
            ("x", _("X"), wx.TextCtrl, (self, -1, ""), {}),
            ("y1", _("Y1"), wx.TextCtrl, (self, -1, ""), {}),
            ("y2", _("Y2"), wx.TextCtrl, (self, -1, ""), {}),
        ]

        BoxedPanel.__init__(self, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        self.x_editor.SetToolTipString(_("Enter a list of values."))
        self.y1_editor.SetToolTipString(_("Enter a list of values."))
        self.y2_editor.SetToolTipString(_("Enter a list of values."))

    def __bindings(self):
        """Binds events ton handlers"""

        self.Bind(wx.EVT_TEXT, self.OnXText, self.x_editor)
        self.Bind(wx.EVT_TEXT, self.OnY1Text, self.y1_editor)

    # Handlers
    # --------

    def OnXText(self, event):
        """Event handler for x_text_ctrl"""

        self.chart_data["x_data"] = ast.literal_eval(event.GetString())
        post_command_event(self, self.DrawChartMsg)

    def OnY1Text(self, event):
        """Event handler for y1_text_ctrl"""

        self.chart_data["y1_data"] = ast.literal_eval(event.GetString())
        post_command_event(self, self.DrawChartMsg)


class ChartAxisLinePanel(BoxedPanel):
    """Panel for line style entry"""

    def __init__(self, *args, **kwargs):

        # Custom data
        _styles = map(unicode, xrange(len(PenStyleComboBox.pen_styles)))
        _widths = map(unicode, xrange(12))

        kwargs["box_label"] = _("Line")

        pen_style_combo_args = (self, -1), {"choices": _styles},
        colorselect_args = (self, -1, unichr(0x2500) * 6), {"size": (80, 25)}
        pen_width_combo_args = (self,), {"choices": _widths,
                                "style": wx.CB_READONLY, "size": (50, -1)}

        kwargs["widgets"] = [
            ("style", _("Style"), PenStyleComboBox) + pen_style_combo_args,
            ("color", _("Color"), csel.ColourSelect) + colorselect_args,
            ("width", _("Width"), PenWidthComboBox) + pen_width_combo_args,
        ]

        BoxedPanel.__init__(self, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        # Set controls to default values
        self.width_editor.SetSelection(self.chart_data["line_width"])

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_COMBOBOX, self.OnWidth, self.width_editor)
        self.color_editor.Bind(csel.EVT_COLOURSELECT, self.OnColor)

    # Handlers
    # --------

    def OnWidth(self, event):
        """Line width event handler"""

        self.chart_data["line_width"] = int(event.GetSelection())
        post_command_event(self, self.DrawChartMsg)

    def OnColor(self, event):
        """Line color event handler"""

        self.chart_data["line_color"] = \
                tuple(i / 255.0 for i in event.GetValue().Get())
        post_command_event(self, self.DrawChartMsg)


class ChartAxisMarkerPanel(BoxedPanel):
    """Panel for marker style entry"""

    def __init__(self, *args, **kwargs):

        # Custom data
        _styles = map(unicode, xrange(len(PenStyleComboBox.pen_styles)))

        kwargs["box_label"] = _("Marker")

        pen_style_combo_args = (self, -1), {"choices": _styles},
        colorselect_args = (self, -1), {"size": (80, 25)}

        kwargs["widgets"] = [
            ("style", _("Style"), PenStyleComboBox) + pen_style_combo_args,
            ("front", _("Front"), csel.ColourSelect) + colorselect_args,
            ("back", _("Back"), csel.ColourSelect) + colorselect_args,
        ]

        BoxedPanel.__init__(self, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        # Set controls to default values
        pass

    def __bindings(self):
        """Binds events to handlers"""

        pass

    # Handlers
    # --------


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

        self.chart_axis_data_panel = \
            ChartAxisDataPanel(self, -1, chart_data=self.chart_data)
        self.chart_axis_line_panel = \
            ChartAxisLinePanel(self, -1, chart_data=self.chart_data)
        self.chart_axis_marker_panel = \
            ChartAxisMarkerPanel(self, -1, chart_data=self.chart_data)

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

    def __do_layout(self):
        sizer_1 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_4 = wx.FlexGridSizer(1, 1, 0, 0)
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
        sizer_4.Add(self.chart_axis_line_panel, 1, wx.ALL | wx.EXPAND, 2)
        sizer_4.Add(self.chart_axis_marker_panel, 1, wx.ALL | wx.EXPAND, 2)
        sizer_4.AddGrowableCol(0)
        sizer_series_staticbox.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_1.Add(self.figure_canvas, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)
        self.SetSizer(sizer_1)
        sizer_1.AddGrowableRow(0)
        sizer_1.AddGrowableCol(0)
        self.Layout()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(self.EVT_CMD_DRAW_CHART, self.OnDrawChart)

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


    def OnDrawChart(self, event):
        """Figure drawing event handler"""

        self.draw_chart(self.chart_data)