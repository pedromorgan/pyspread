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

# Architecture
# ------------
#
# Create widgets <Type>Editor for each type
# types are: bool, int, str, color, iterable, marker_style, line_style
# Each widget has a get_code method and a set_code method
#
# A SeriesBoxPanel is defined by:
# [panel_label, (matplotlib_key, widget, label, tooltip), ...]
#
# A <Seriestype>AttributesPanel(SeriesPanelBase) is defined by:
# [seriestype_key, SeriesBoxPanel, ...]
# It is derived from SeriesBasePanel and provides a widgets attribute
#
# SeriesPanelBase provides a method
# __iter__ that yields (key, code) for each widget
#
# SeriesPanel provides a TreeBook of series types
# It is defined by:
# [(seriestype_key, seriestype_label, seriestype_image,
#                                     <Seriestype>AttributesPanel), ...]
#
# AllSeriesPanel provides a flatnotebook with one tab per series
#
# FigureAttributesPanel is equivalent to a <Seriestype>AttributesPanel
#
# FigurePanel provides a matplotlib chart drawing
#
# ChartDialog provides FigureAttributesPanel, Flatnotebook of SeriesPanels,
#                      FigurePanel

import ast
from copy import copy
from itertools import izip

import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import wx.lib.colourselect as csel
from wx.lib.intctrl import IntCtrl, EVT_INT
import wx.lib.agw.flatnotebook as fnb
import numpy

from _widgets import PenWidthComboBox, LineStyleComboBox, MarkerStyleComboBox
from _events import post_command_event, ChartDialogEventMixin
import src.lib.i18n as i18n
import src.lib.charts as charts
from src.lib.parsers import parse_dict_strings, color2code, code2color
from icons import icons

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


# --------------
# Editor widgets
# --------------

class EditorCodeMixin(object):
    """Mixin class that provides standard interfaces for Editor<type> classes

    Provides
    --------

    Methods:

    * get_code
    * set_code
    Properties:

    * code

    """

    def get_code(self):
        """Returns code representation of value of widget"""

        return self.GetValue()

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of widget value

        """

        self.SetValue(code)

    # Properties

    code = property(get_code, set_code)


class BoolEditor(wx.CheckBox, EditorCodeMixin):
    """Editor widget for bool values"""

    def __init__(self, *args, **kwargs):
        wx.CheckBox.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_CHECKBOX, self.OnChecked)

    def get_code(self):
        """Returns '0' or '1'"""

        return repr(self.GetValue())

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of bool value

        """

        self.SetValue(bool(code))

    # Handlers

    def OnChecked(self, event):
        """Check event handler"""

        post_command_event(self, self.DrawChartMsg)


class IntegerEditor(IntCtrl, EditorCodeMixin):
    """Editor widget for integer values"""

    def __init__(self, *args, **kwargs):
        IntCtrl.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(EVT_INT, self.OnInt)

    def get_code(self):
        """Returns string representation of Integer"""

        return repr(self.GetValue())

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of integer value

        """

        self.SetValue(int(code))

    # Handlers

    def OnInt(self, event):
        """Check event handler"""

        post_command_event(self, self.DrawChartMsg)


class StringEditor(wx.TextCtrl, EditorCodeMixin):
    """Editor widget for string values"""

    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_TEXT, self.OnText)

    # Handlers

    def OnText(self, event):
        """Text entry event handler"""

        post_command_event(self, self.DrawChartMsg)


class ColorEditor(csel.ColourSelect, EditorCodeMixin):
    """Editor widget for 3-tuples of floats that represent color"""

    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(csel.EVT_COLOURSELECT, self.OnColor)

    def get_code(self):
        """Returns string representation of Integer"""

        return color2code(self.GetValue())

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tString representation of 3 tuple of float

        """

        self.SetColour(code2color(code))

    # Handlers

    def OnColor(self, event):
        """Check event handler"""

        post_command_event(self, self.DrawChartMsg)


class StyleEditorMixin(object):
    """Mixin class for stzle editors that are based on MatplotlibStyleChoice"""

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_CHOICE, self.OnStyle)

    def get_code(self):
        """Returns string representation of Integer"""

        return self.get_style_code(self.StringSelection)

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tMarker style string

        """

        self.StringSelection = self.get_label(code)

    # Handlers
    # --------

    def OnStyle(self, event):
        """Marker style event handler"""

        post_command_event(self, self.DrawChartMsg)


class MarkerStyleEditor(MarkerStyleComboBox, EditorCodeMixin,
                        StyleEditorMixin):
    """Editor widget for marker style string values"""

    def __init__(self, *args, **kwargs):
        MarkerStyleComboBox.__init__(self, *args, **kwargs)

        self.__bindings()


class LineStyleEditor(LineStyleComboBox, EditorCodeMixin, StyleEditorMixin):
    """Editor widget for line style string values"""

    def __init__(self, *args, **kwargs):
        LineStyleComboBox.__init__(self, *args, **kwargs)

        self.__bindings()


# -------------
# Panel widgets
# -------------

class SeriesBoxPanel(wx.Panel):
    """Box panel that contains labels and widgets

    Parameters
    ----------

    * panel_label: String
    \tLabel that is displayed left of the widget
    * labels: List of strings
    \tWidget labels
    * widgets: List of class instances
    \tWidget instance list must be as long as labels

    """

    def __init__(self, parent, box_label, labels, widgets):

        wx.Panel.__init__(self, parent, -1)

        self.staticbox = wx.StaticBox(self, -1, box_label)

        self.__do_layout(labels, widgets)

    def __do_layout(self, labels, widgets):
        box_sizer = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer = wx.FlexGridSizer(1, 2, 0, 0)

        for label, widget in izip(labels, widgets):
            grid_sizer.Add(wx.StaticText(self, -1, label))
            grid_sizer.Add(widget)

        grid_sizer.AddGrowableCol(1)
        box_sizer.Add(grid_sizer, 1, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(box_sizer)

        self.Layout()


class SeriesAttributesPanelBase(wx.Panel):
    """Base class for <Seriestype>AttributesPanel and FigureAttributesPanel"""

    def __init__(self, parent):

        self.boxes = []
        self.widgets = {}

        for box_label, keys in self.boxes:

            labels = []
            widgets = []

            for key in keys:
                widget_label, widget_cls, widget_default = self.data[key]
                widget = widget_cls(self, -1)
                widget.code = widget_default

                widgets.append(widget)
                labels.append(widget_label)

                self.widgets[key] = widget

            self.boxes.append(SeriesBoxPanel(self, box_label, labels, widgets))

        self.__do_layout()

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        for box in self.boxes:
            main_sizer.Add(box, 1, wx.ALL | wx.EXPAND, 2)

        main_sizer.AddGrowableCol(0)

        self.SetSizer(main_sizer)

        self.Layout()

    def __iter__(self):
        """Yields (key, code) for each widget"""

        for widget in self.widgets:
            yield widget.code


class PlotAttributesPanel(SeriesAttributesPanelBase):
    """Panel that provides plot series attributes in multiple boxed panels"""

    # Data for series plot
    # matplotlib_key, label, widget_cls, default_code

    data = {
        "name": (_("Series name"), StringEditor, ""),
        "xdata":  (_("X"), StringEditor, ""),
        "ydata":  (_("Y"), StringEditor, ""),
        "linestyle":  (_("Style"), LineStyleEditor, '-'),
        "linewidth":  (_("Width"), IntegerEditor, "1"),
        "color":  (_("Color"), ColorEditor, "(0, 0, 0)"),
        "marker":  (_("Style"), MarkerStyleEditor, ""),
        "markersize":  (_("Size"), IntegerEditor, "5"),
        "markerfacecolor": (_("Face color"), ColorEditor, "(0, 0, 0)"),
        "markeredgecolor": (_("Edge color"), ColorEditor, "(0, 0, 0)"),
    }

    # Boxes and their widgets' matplotlib_keys
    # label, [matplotlib_key, ...]

    boxes = [
        (_("Data"), ["xdata", "ydata"]),
        (_("Line"), ["linestyle", "linewidth", "color"]),
        (_("Marker"), ["marker", "markersize", "markerfacecolor",
                       "markeredgecolor"]),
    ]


class BarAttributesPanel(SeriesAttributesPanelBase):
    """Panel that provides bar series attributes in multiple boxed panels"""

    # Data for bar plot
    # matplotlib_key, label, widget_cls, default_code

    data = {
        "name": (_("Series name"), StringEditor, ""),
        "left": (_("Left positions"), StringEditor, ""),
        "height": (_("Bar heights"), StringEditor, ""),
        "width": (_("Bar widths"), StringEditor, ""),
        "bottom": (_("Bar bottoms"), StringEditor, ""),
        "color": (_("Bar color"), ColorEditor, "(0, 0, 0)"),
        "edgecolor": (_("Edge color"), ColorEditor, "(0, 0, 0)"),
    }

    # Boxes and their widgets' matplotlib_keys
    # label, [matplotlib_key, ...]

    boxes = [
        (_("Data"), ["left", "height", "width", "bottom"]),
        (_("Bar"), ["color", "edgecolor"]),
    ]


class FigureAttributesPanel(SeriesAttributesPanelBase):
    """Panel that provides figure attributes in multiple boxed panels"""

    # Data for figure
    # matplotlib_key, label, widget_cls, default_code

    data = {
        "xlabel": (_("Label"), StringEditor, ""),
        "xlim": (_("Limits"), StringEditor, ""),
        "xscale": (_("Log"), BoolEditor, "False"),
        "ylabel": (_("Label"), StringEditor, ""),
        "yscale": (_("Log"), BoolEditor, "False"),
        "ylim": (_("Limits"), StringEditor, ""),
    }

    # Boxes and their widgets' matplotlib_keys
    # label, [matplotlib_key, ...]

    boxes = [
        (_("X-Axis"), ["xlabel", "xlim", "xscale"]),
        (_("Y-Axis"), ["ylabel", "ylim", "yscale"]),
    ]


class SeriesPanel(wx.Panel):
    """Panel that holds attribute information for one series of the chart"""

    plot_types = [
        {"type": "plot", "panel_class": PlotAttributesPanel},
        {"type": "bar", "panel_class": BarAttributesPanel},
    ]

    def __init__(self, grid, series_dict):

        self.grid = grid

        wx.Panel.__init__(self, grid, -1)

        self.chart_type_book = wx.Treebook(self, -1, style=wx.BK_LEFT)
        self.il = wx.ImageList(24, 24)

        # Add plot panels

        for i, plot_type_dict in enumerate(self.plot_types):
            plot_type = plot_type_dict["type"]
            PlotPanelClass = plot_type_dict["panel_class"]

            series_data = {}
            if plot_type == series_dict["series_type"]:
                series_data.update(series_dict)
                self.plot_type = plot_type

            plot_panel = PlotPanelClass(self, -1, series_data)
            self.chart_type_book.AddPage(plot_panel, plot_type, imageId=i)
            self.il.Add(icons[plot_type_dict["type"]])

        self._properties()
        self.__bindings()
        self.__do_layout()

    def _properties(self):
        self.chart_type_book.SetImageList(self.il)

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)
        main_sizer.Add(self.chart_type_book, 1, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(main_sizer)

        self.Layout()

    def get_plot_panel(self):
        """Returns current plot_panel"""

        plot_type_no = self.chart_type_book.GetSelection()
        return self.chart_type_book.GetPage(plot_type_no)

    def set_plot_panel(self, plot_type_no):
        """Sets current plot_panel to plot_type_no"""

        self.chart_type_book.SetPage(plot_type_no)

    plot_panel = property(get_plot_panel, set_plot_panel)

    def get_plot_type(self):
        """Returns current plot type"""

        return self.plot_types[self.plot_panel]["type"]

    def set_plot_type(self, plot_type):
        """Sets plot type"""

        ptypes = [pt["type"] for pt in self.plot_types]
        self.plot_panel = ptypes.index(plot_type)

    plot_type = property(get_plot_type, set_plot_type)


class AllSeriesPanel(wx.Panel):
    """Panel that holds series panels for all series of the chart"""

    def __init__(self, grid, series_list):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | \
                        wx.THICK_FRAME

        wx.Dialog.__init__(self, grid, style=style)

        agwstyle = fnb.FNB_NODRAG | fnb.FNB_DROPDOWN_TABS_LIST | fnb.FNB_BOTTOM
        self.series_notebook = fnb.FlatNotebook(self, -1, agwStyle=agwstyle)

        # Add as many tabs as there are series in code

        for series_dict in series_list:
            series_panel = SeriesPanel(self, grid, series_dict)
            self.series_notebook.AddPage(series_panel, series_dict["name"])

        # Update widget content

        self.update(series_list)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnSeriesChanged)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnSeriesDeleted)

    def update(self, series_list):
        """Updates widget content from series_list

        Parameters
        ----------
        series_list: List of dict
        \tList of dicts with data from all series

        """

        raise NotImplementedError

    # Handlers
    # --------

    def OnSeriesChanged(self, event):
        """FlatNotebook change event handler"""

        selection = event.GetSelection()

        if selection == self.series_notebook.GetPageCount() - 1:
            # Add new series
            new_panel = SeriesPanel(self, -1)
            self.series_notebook.InsertPage(selection, new_panel, _("Series"))

        event.Skip()

    def OnSeriesDeleted(self, event):
        """FlatNotebook closing event handler"""

        # Redraw Chart
        post_command_event(self, self.DrawChartMsg)

        event.Skip()


class FigurePanel(wx.Panel):
    """Panel that draws a matplotlib figure_canvas"""

    def __init__(self, figure):

        # Set figure_canvas

        self.figure_canvas = self._get_figure_canvas(figure)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.figure_canvas.SetMinSize((100, 100))

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        main_sizer.Add(self.figure_canvas, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableCol(1)

        self.SetSizer(main_sizer)

        self.Layout()

    def _get_figure_canvas(self, figure):
        """Returns figure canvas"""

        return FigureCanvasWxAgg(self, -1, self.figure)

    def update(self, figure):
        """Updates figure on data change

        Parameters
        ----------
        * figure: matplotlib.figure.Figure
        \tMatplotlib figure object that is displayed in self

        """

        self.figure_canvas = self._get_figure_canvas(figure)
        self.figure_canvas.draw()


class ChartDialog(wx.Dialog, ChartDialogEventMixin):
    """Chart dialog for generating chart generation strings"""

    def __init__(self, grid):
        wx.Dialog.__init__(self, grid, -1)

        self.grid = grid
        self.key = self.grid.actions.cursor

        self.update_widgets()

    def _get_figure(self):
        """Returns figure from code"""

    def set_code(self):
        """Update widgets from code"""

    def get_code(self):
        """Returns code from widgets"""

    code = property(set_code, get_code)




















class LabeledWidgetPanel(wx.Panel, ChartDialogEventMixin):
    """Base class for boxed panels with labeled widgets"""

    def __init__(self, *args, **kwargs):

        self.parent = args[0]

        try:
            self.series_data = kwargs.pop("series_data")
        except KeyError:
            pass

        try:
            self.axes_data = kwargs.pop("axes_data")
        except KeyError:
            pass

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

    def _color_from_string(self, color_string):
        """Returns wx.Colour from given tuple string"""

        color_tuple = self.parent.get_series_tuple(color_string)
        color_tuple_int = map(lambda x: int(x * 255), color_tuple)
        return wx.Colour(*color_tuple_int)


class AxesLabelPanel(LabeledWidgetPanel):
    """Panel for data entry for axes label"""

    def __init__(self, *args, **kwargs):

        # Custom data
        kwargs["box_label"] = _("Labels")

        kwargs["widgets"] = [
            ("xlabel", _("X"), wx.TextCtrl,
             (self, -1, kwargs["axes_data"]["xlabel"]), {}),
            ("ylabel", _("Y"), wx.TextCtrl,
             (self, -1, kwargs["axes_data"]["ylabel"]), {}),
        ]

        LabeledWidgetPanel.__init__(self, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        self.xlabel_editor.SetToolTipString(_("Enter label for X-axis."))
        self.ylabel_editor.SetToolTipString(_("Enter label for Y-axis."))

    def __bindings(self):
        """Binds events ton handlers"""

        self.Bind(wx.EVT_TEXT, self.OnXLabelText, self.xlabel_editor)
        self.Bind(wx.EVT_TEXT, self.OnYLabelText, self.ylabel_editor)

    # Handlers
    # --------

    def OnXLabelText(self, event):
        """Event handler for xlabel_editor"""

        self.axes_data["xlabel"] = event.GetString()

        post_command_event(self, self.DrawChartMsg)

    def OnYLabelText(self, event):
        """Event handler for ylabel_editor"""

        self.axes_data["ylabel"] = event.GetString()

        post_command_event(self, self.DrawChartMsg)


class ChartAxisDataPanel(LabeledWidgetPanel):
    """Panel for data entry for chart axis"""

    def __init__(self, *args, **kwargs):
        # Different chart tzpes have different names for x and y data
        series_mapping = kwargs.pop("series_mapping")
        xdata = series_mapping["x"]
        ydata = series_mapping["y"]

        # Custom data
        kwargs["box_label"] = _("Data")

        kwargs["widgets"] = [
            ("x", _("X"), wx.TextCtrl,
             (self, -1, kwargs["series_data"][xdata]), {}),
            ("y", _("Y"), wx.TextCtrl,
             (self, -1, kwargs["series_data"][ydata]), {}),
        ]

        LabeledWidgetPanel.__init__(self, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        self.x_editor.SetToolTipString(
            _("Enter a list of X values (optional)."))
        self.y_editor.SetToolTipString(_("Enter a list of Y values."))

    def __bindings(self):
        """Binds events ton handlers"""

        self.Bind(wx.EVT_TEXT, self.OnXText, self.x_editor)
        self.Bind(wx.EVT_TEXT, self.OnYText, self.y_editor)

    # Handlers
    # --------

    def OnXText(self, event):
        """Event handler for x_editor"""

        self.series_data["xdata"] = event.GetString()

        post_command_event(self, self.DrawChartMsg)

    def OnYText(self, event):
        """Event handler for y_editor"""

        self.series_data["ydata"] = event.GetString()

        post_command_event(self, self.DrawChartMsg)


class ChartAxisLinePanel(LabeledWidgetPanel):
    """Panel for line style entry"""

    def __init__(self, *args, **kwargs):

        # Custom data
        _widths = map(unicode, xrange(12))

        kwargs["box_label"] = _("Line")

        pen_style_combo_args = (self, -1), {}
        colorselect_args = (self, -1, unichr(0x2500) * 6), {"size": (80, 25)}
        pen_width_combo_args = (self,), {"choices": _widths,
                                "style": wx.CB_READONLY, "size": (50, -1)}

        kwargs["widgets"] = [
            ("style", _("Style"), LineStyleComboBox) + pen_style_combo_args,
            ("color", _("Color"), csel.ColourSelect) + colorselect_args,
            ("width", _("Width"), PenWidthComboBox) + pen_width_combo_args,
        ]

        LabeledWidgetPanel.__init__(self, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        # Set controls to default values
        self.width_editor.SetSelection(int(self.series_data["linewidth"]))

    def __bindings(self):
        """Binds events to handlers"""

        self.style_editor.Bind(wx.EVT_CHOICE, self.OnStyle)
        self.Bind(wx.EVT_COMBOBOX, self.OnWidth, self.width_editor)
        self.color_editor.Bind(csel.EVT_COLOURSELECT, self.OnColor)

    # Handlers
    # --------

    def OnStyle(self, event):
        """Line style event handler"""

        line_style_code = self.style_editor.get_code(event.GetString())
        self.series_data["linestyle"] = repr(line_style_code)
        post_command_event(self, self.DrawChartMsg)

    def OnWidth(self, event):
        """Line width event handler"""

        self.series_data["linewidth"] = repr(event.GetSelection())
        post_command_event(self, self.DrawChartMsg)

    def OnColor(self, event):
        """Line color event handler"""

        self.series_data["color"] = \
                repr(tuple(i / 255.0 for i in event.GetValue().Get()))
        post_command_event(self, self.DrawChartMsg)


class ChartAxisBarPanel(LabeledWidgetPanel):
    """Panel for bar style entry"""

    def __init__(self, *args, **kwargs):

        kwargs["box_label"] = _("Bar")

        default_args = (self, -1), {}
        colorselect_args = (self, -1, unichr(0x2500) * 6), {"size": (80, 25)}

        kwargs["widgets"] = [
            ("left", _("Left values"), wx.TextCtrl) + default_args,
            ("color", _("Color"), csel.ColourSelect) + colorselect_args,
            ("edgecolor", _("Edge color"),
                                csel.ColourSelect) + colorselect_args,
            ("width", _("Bar width"), wx.TextCtrl) + default_args,
            ("log", _("Log scale"), wx.CheckBox) + default_args,
        ]

        LabeledWidgetPanel.__init__(self, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        # Set controls to default values
        self.width_editor.SetValue(self.series_data["width"])

    def __bindings(self):
        """Binds events to handlers"""

        self.left_editor.Bind(wx.EVT_TEXT, self.OnLeft)
        self.color_editor.Bind(csel.EVT_COLOURSELECT, self.OnColor)
        self.edgecolor_editor.Bind(csel.EVT_COLOURSELECT, self.OnEdgeColor)
        self.width_editor.Bind(wx.EVT_TEXT, self.OnLeft)
        self.log_editor.Bind(wx.EVT_CHECKBOX, self.OnLog)

    # Handlers
    # --------

    def OnLeft(self, event):
        """Left values event handler"""

        self.series_data["left"] = repr(event.GetString())
        post_command_event(self, self.DrawChartMsg)

    def OnColor(self, event):
        """Bar background color event handler"""

        self.series_data["color"] = \
                repr(tuple(i / 255.0 for i in event.GetValue().Get()))
        post_command_event(self, self.DrawChartMsg)

    def OnEdgeColor(self, event):
        """Edge color event handler"""

        self.series_data["edgecolor"] = \
                repr(tuple(i / 255.0 for i in event.GetValue().Get()))
        post_command_event(self, self.DrawChartMsg)

    def OnWidth(self, event):
        """Bar width event handler"""

        self.series_data["linewidth"] = repr(event.GetString())
        post_command_event(self, self.DrawChartMsg)

    def OnLog(self, event):
        """Logarithmic scale event handler"""

        self.series_data["log"] = repr(event.IsChecked())
        post_command_event(self, self.DrawChartMsg)


class ChartAxisMarkerPanel(LabeledWidgetPanel):
    """Panel for marker style entry"""

    def __init__(self, parent, *args, **kwargs):

        self.parent = parent
        kwargs["box_label"] = _("Marker")

        marker_style_combo_args = (self, -1), {}
        colorselect_args = (self, -1), {"size": (80, 25)}
        intctrl_args = (self, -1, 0, None), {}

        kwargs["widgets"] = [
            ("style", _("Style"), MarkerStyleComboBox) +
                                  marker_style_combo_args,
            ("size", _("Size"), IntCtrl) + intctrl_args,
            ("face_color", _("Face"), csel.ColourSelect) + colorselect_args,
            ("edge_color", _("Edge"), csel.ColourSelect) + colorselect_args,
        ]

        LabeledWidgetPanel.__init__(self, parent, *args, **kwargs)

        self.__set_properties()
        self.__bindings()

    def __set_properties(self):
        # Set controls to default values

        marker_style_code = self.series_data["marker"][1:-1]
        marker_style_label = self.style_editor.get_label(marker_style_code)
        self.style_editor.SetStringSelection(marker_style_label)

        self.size_editor.SetValue(int(self.series_data["markersize"]))

        face_color_string = self.series_data["markerfacecolor"]
        face_color = self._color_from_string(face_color_string)
        self.face_color_editor.SetColour(face_color)

        edge_color_string = self.series_data["markeredgecolor"]
        edge_color = self._color_from_string(edge_color_string)
        self.edge_color_editor.SetColour(edge_color)

    def __bindings(self):
        """Binds events to handlers"""

        self.style_editor.Bind(wx.EVT_CHOICE, self.OnStyle)
        self.size_editor.Bind(EVT_INT, self.OnSize)
        self.face_color_editor.Bind(csel.EVT_COLOURSELECT, self.OnFaceColor)
        self.edge_color_editor.Bind(csel.EVT_COLOURSELECT, self.OnEdgeColor)

    # Handlers
    # --------

    def OnStyle(self, event):
        """Marker style event handler"""

        marker_style_code = self.style_editor.get_code(event.GetString())
        self.series_data["marker"] = repr(marker_style_code)
        post_command_event(self, self.DrawChartMsg)

    def OnSize(self, event):
        """Marker size event"""

        self.series_data["markersize"] = repr(event.GetValue())
        post_command_event(self, self.DrawChartMsg)

    def OnEdgeColor(self, event):
        """Marker front color event handler"""

        self.series_data["markeredgecolor"] = \
                repr(tuple(i / 255.0 for i in event.GetValue().Get()))
        post_command_event(self, self.DrawChartMsg)

    def OnFaceColor(self, event):
        """Marker back color event handler"""

        self.series_data["markerfacecolor"] = \
                repr(tuple(i / 255.0 for i in event.GetValue().Get()))
        post_command_event(self, self.DrawChartMsg)


class AxesPanel(wx.Panel):
    """Panel that holds widgets for axes"""

    def __init__(self, parent, __id, axes_data=None):

        wx.Panel.__init__(self, parent, __id)

        # Default data for series plot

        self.axes_data = {
            "xlabel": u"''",
            "ylabel": u"''",
        }

        if axes_data is not None:
            self.axes_data.update(axes_data)

        # Data types for keys

        self.series_keys = []
        self.string_keys = ["xlabel", "ylabel"]
        self.float_keys = []
        self.bool_keys = []

        # Widgets

        self.label_panel = AxesLabelPanel(self, -1, axes_data=self.axes_data)

        self.__do_layout()

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        main_sizer.Add(self.label_panel, 1, wx.ALL | wx.EXPAND, 2)
        main_sizer.AddGrowableCol(0)

        self.SetSizer(main_sizer)

        self.Layout()


class BarPanel(wx.Panel):
    """Panel that holds widgets for one bar series"""

    def __init__(self, parent, __id, series_data=None):

        wx.Panel.__init__(self, parent, __id)

        self.get_series_tuple = parent.parent.get_series_tuple

        # Default data for series plot

        self.series_data = {
            "type": "'bar'",
            "left": u"",
            "height": u"",
            "width": u"",
            "bottom": u"",
            "color": u"(0, 0, 0)",
            "edgecolor": u"(0, 0, 0)",
            "log": u"False",
        }

        if series_data is not None:
            self.series_data.update(series_data)

        # Data types for keys

        self.series_keys = ["left", "height", "width", "bottom",
                            "color", "edgecolor"]
        self.string_keys = ["type"]
        self.float_keys = []
        self.bool_keys = ["log"]

        # Widgets
        series_mapping = {"x": "bottom", "y": "height"}
        self.data_panel = \
            ChartAxisDataPanel(self, -1, series_data=self.series_data,
                               series_mapping=series_mapping)
        self.bar_panel = \
            ChartAxisBarPanel(self, -1, series_data=self.series_data)

        self.__do_layout()

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableCol(1)

        main_sizer.Add(self.data_panel, 1, wx.ALL | wx.EXPAND, 2)
        main_sizer.Add(self.bar_panel, 1, wx.ALL | wx.EXPAND, 2)
        main_sizer.AddGrowableCol(0)

        self.SetSizer(main_sizer)

        self.Layout()


class PlotPanel(wx.Panel):
    """Panel that holds widgets for one plot series"""

    def __init__(self, parent, __id, series_data=None):

        wx.Panel.__init__(self, parent, __id)

        self.get_series_tuple = parent.parent.get_series_tuple

        # Default data for series plot

        self.series_data = {
            "type": "'plot'",
            "xdata": u"",
            "ydata": u"",
            "linestyle": u"'-'",
            "linewidth": u"1",
            "color": u"(0, 0, 0)",
            "marker": u"''",
            "markersize": u"5",
            "markerfacecolor": u"(0, 0, 0)",
            "markeredgecolor": u"(0, 0, 0)",
        }

        if series_data is not None:
            self.series_data.update(series_data)

        # Data types for keys

        self.series_keys = ["xdata", "ydata", "color", "markerfacecolor",
                            "markeredgecolor"]
        self.string_keys = ["type", "linestyle", "marker"]
        self.float_keys = ["markersize"]
        self.bool_keys = []

        # Widgets
        series_mapping = {"x": "xdata", "y": "ydata"}
        self.data_panel = \
            ChartAxisDataPanel(self, -1, series_data=self.series_data,
                               series_mapping=series_mapping)
        self.line_panel = \
            ChartAxisLinePanel(self, -1, series_data=self.series_data)
        self.marker_panel = \
            ChartAxisMarkerPanel(self, -1, series_data=self.series_data)

        self.__do_layout()

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableCol(1)

        main_sizer.Add(self.data_panel, 1, wx.ALL | wx.EXPAND, 2)
        main_sizer.Add(self.line_panel, 1, wx.ALL | wx.EXPAND, 2)
        main_sizer.Add(self.marker_panel, 1, wx.ALL | wx.EXPAND, 2)
        main_sizer.AddGrowableCol(0)

        self.SetSizer(main_sizer)

        self.Layout()


class SeriesPanel(wx.Panel):
    """Panel that holds widgets for one series"""

    plot_type_data = [
        {"type": "plot", "panel_class": PlotPanel},
        {"type": "bar", "panel_class": BarPanel},
    ]

    def __init__(self, parent, __id, series_data=None):

        self.parent = parent

        wx.Panel.__init__(self, parent, __id)

        self.chart_type_book = wx.Treebook(self, -1, style=wx.BK_LEFT)

        # Add plot panels

        for i, plot_type_dict in enumerate(self.plot_type_data):
            plot_type = plot_type_dict["type"]
            PlotPanelClass = plot_type_dict["panel_class"]
            plot_panel = PlotPanelClass(self, -1, series_data)
            self.chart_type_book.AddPage(plot_panel, plot_type, imageId=i)

        self._properties()
        self.__bindings()
        self.__do_layout()

    def _properties(self):
        self.il = wx.ImageList(24, 24)
        for plot_type_dict in self.plot_type_data:
            self.il.Add(icons[plot_type_dict["type"]])
        self.chart_type_book.SetImageList(self.il)

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnChartTypeSelected,
                  self.chart_type_book)

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)
        main_sizer.Add(self.chart_type_book, 1, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(main_sizer)

        self.Layout()

    def get_current_plot_panel(self):
        """Returns current plot_panel"""

        plot_type_no = self.chart_type_book.GetSelection()
        return self.chart_type_book.GetPage(plot_type_no)

    # Handlers
    # --------

    def OnChartTypeSelected(self, event):
        """Chart type selection ListCtrl selection event handler"""

        self.plot_panel.series_data["type"] = \
                repr(self.plot_types[event.m_itemIndex])

        event.Skip()


class ChartDialog(wx.Dialog, ChartDialogEventMixin):
    """Chart dialog for generating chart generation strings"""

    series = []

    def __init__(self, parent, code, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | \
                        wx.THICK_FRAME
        self.grid = parent

        wx.Dialog.__init__(self, parent, **kwds)

        agwstyle = fnb.FNB_NODRAG | fnb.FNB_DROPDOWN_TABS_LIST | fnb.FNB_BOTTOM
        self.series_notebook = fnb.FlatNotebook(self, -1, agwStyle=agwstyle)

        if code[:7] == "charts.":
            # If chart data is present build the chart
            key = self.grid.actions.cursor
            self.figure = self.grid.code_array._eval_cell(key, code)

            # Get data from figure
            code_param_string = code.split("(", 1)[1][:-1]
            code_param_list = list(parse_dict_strings(code_param_string))
            code_param = []

            # The first item in the code param list is axes data
            axes_param_string = code_param_list.pop(0)
            axes_param_list = list(parse_dict_strings(axes_param_string[1:-1]))
            axes_param = dict((ast.literal_eval(k), v) for k, v in
                            zip(axes_param_list[::2], axes_param_list[1::2]))

            for series_param_string in code_param_list:
                series_param_list = \
                    list(parse_dict_strings(series_param_string[1:-1]))
                series_param = dict((ast.literal_eval(k), v) for k, v in
                    zip(series_param_list[::2], series_param_list[1::2]))
                code_param.append(series_param)

            self.axes_panel = AxesPanel(self, -1, axes_param)

            for series_param in code_param:
                series_panel = SeriesPanel(self, -1, series_param)

                self.series_notebook.AddPage(series_panel, _("Series"))

                for key in series_param:
                    plot_panel = series_panel.get_current_plot_panel()
                    plot_panel.series_data[key] = series_param[key]

        else:
            # Use default values
            self.axes_panel = AxesPanel(self, -1)
            plot_panel = SeriesPanel(self, -1)
            self.series_notebook.AddPage(plot_panel, _("Series"))
            chart_data = self.eval_chart_data()
            self.figure = charts.ChartFigure(*chart_data)

        self.series_notebook.AddPage(wx.Panel(self, -1), _("+"))

        # end series creation

        self.cancel_button = wx.Button(self, wx.ID_CANCEL)
        self.ok_button = wx.Button(self, wx.ID_OK)

        self.figure_canvas = FigureCanvasWxAgg(self, -1, self.figure)

        self.__set_properties()
        self.__do_layout()
        self.__bindings()

        # Draw figure initially
        post_command_event(self, self.DrawChartMsg)

    def __set_properties(self):
        self.SetTitle(_("Insert chart"))
        self.SetSize((1000, 400))
        self.figure_canvas.SetMinSize((400, 300))

        self.axes_staticbox = wx.StaticBox(self, -1, _(u"Axes"))
        self.series_staticbox = wx.StaticBox(self, -1, _(u"Series"))

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(2, 3, 0, 0)
        axes_box_sizer = wx.StaticBoxSizer(self.axes_staticbox, wx.HORIZONTAL)
        series_box_sizer = wx.StaticBoxSizer(self.series_staticbox,
                                             wx.HORIZONTAL)
        button_sizer = wx.FlexGridSizer(1, 3, 0, 3)

        main_sizer.Add(axes_box_sizer, 1, wx.EXPAND, 0)
        main_sizer.Add(series_box_sizer, 1, wx.EXPAND, 0)
        main_sizer.Add(self.figure_canvas, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)
        main_sizer.Add(button_sizer, wx.ALL | wx.EXPAND, 3)
        main_sizer.AddGrowableRow(0)
        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableCol(1)

        axes_box_sizer.Add(self.axes_panel, 1, wx.EXPAND, 0)
        series_box_sizer.Add(self.series_notebook, 1, wx.EXPAND, 0)

        button_sizer.Add(self.ok_button, 0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        button_sizer.Add(self.cancel_button, 0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        button_sizer.AddGrowableCol(2)

        self.SetSizer(main_sizer)

        self.Layout()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(self.EVT_CMD_DRAW_CHART, self.OnDrawChart)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnSeriesDeleted)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnSeriesChanged)

    def __disable_controls(self, unneeded_ctrls):
        """Disables the controls that are not needed by chart"""

        for ctrl in unneeded_ctrls:
            ctrl.Disable()

    def get_series_tuple(self, code):
        """Returns series tuples"""

        key = self.grid.actions.cursor

        try:
            result = self.grid.code_array._eval_cell(key, code)
            result_tuple = tuple(numpy.array(result))

        except (TypeError, ValueError):
            result_tuple = tuple(())

        return result_tuple

    def eval_chart_data(self):
        """Returns evaluated content for chart data"""

        def polish_data(panel, data):
            """Polishes data dict"""

            for key in panel.series_keys:
                data[key] = self.get_series_tuple(data[key])

            for key in panel.string_keys:
                data[key] = data[key][1:-1]

            for key in panel.float_keys:
                data[key] = float(data[key])

            for key in panel.bool_keys:
                data[key] = bool(data[key])

        axes_data = copy(self.axes_panel.axes_data)
        polish_data(self.axes_panel, axes_data)

        chart_data = [axes_data]

        no_series = self.series_notebook.GetPageCount() - 1

        for panel_number in xrange(no_series):
            series_panel = self.series_notebook.GetPage(panel_number)
            plot_panel = series_panel.get_current_plot_panel()

            series_data = copy(plot_panel.series_data)
            polish_data(plot_panel, series_data)

            chart_data.append(series_data)

        return chart_data

    def get_figure_code(self):
        """Returns code that generates figure"""

        def get_dict_code(series_keys, data):
            """Builds data string

            data: Dict
            \tThe dict that is converted to a string

            """

            data_code = ""

            for key in data:
                value_str = data[key]

                if key in series_keys:
                    if not value_str or \
                       (value_str[0] != "(" or value_str[-1] != ")"):
                        value_str = "(" + value_str + ")"

                data_code += "'{}': {}, ".format(key, value_str)

            return data_code

        axes_data_code = "{" + \
            get_dict_code(self.axes_panel.series_keys,
                          self.axes_panel.axes_data)[:-2] + \
            "}"

        chart_data_code = ""

        no_series = self.series_notebook.GetPageCount() - 1

        for panel_number in xrange(no_series):
            series_panel = self.series_notebook.GetPage(panel_number)
            sdp_id = series_panel.chart_type_book.GetSelection()
            series_data_panel = series_panel.chart_type_book.GetPage(sdp_id)

            chart_data_code += ", {" + get_dict_code(
                                    series_data_panel.series_keys,
                                    series_data_panel.series_data) + "}"

        chart_data_code = chart_data_code[2:]

        cls_name = charts.ChartFigure.__name__
        return 'charts.{}({}, {})'.format(cls_name, axes_data_code,
                                      chart_data_code)

    # Handlers
    # --------

    def OnSeriesChanged(self, event):
        """FlatNotebook change event handler"""

        selection = event.GetSelection()

        if selection == self.series_notebook.GetPageCount() - 1:
            # Add new series
            new_panel = SeriesPanel(self, -1)
            self.series_notebook.InsertPage(selection, new_panel, _("Series"))

        event.Skip()

    def OnSeriesDeleted(self, event):
        """FlatNotebook closing event handler"""

        # Redraw Chart
        post_command_event(self, self.DrawChartMsg)

        event.Skip()

    def OnDrawChart(self, event):
        """Figure drawing event handler"""

        self.figure.chart_data = self.eval_chart_data()

        try:
            self.figure.draw_chart()
        except ValueError:
            return

        self.figure_canvas.draw()