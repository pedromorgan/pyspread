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
chart_dialog2
=============
"""

import wx
import wx.lib.agw.hypertreelist as htl
import wx.lib.colourselect as csel
from wx.lib.intctrl import IntCtrl
from wx.lib.colourselect import ColourSelect

from matplotlib.pyplot import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

app = wx.App()

from _widgets import LineStyleComboBox, MarkerStyleComboBox
from src.lib.parsers import color2code, code2color, parse_dict_strings
import src.lib.charts as charts

_ = lambda x:x


strftime_doc = _(u"""
Code 	Meaning
%a 	Locale’s abbreviated weekday name.
%A 	Locale’s full weekday name.
%b 	Locale’s abbreviated month name.
%B 	Locale’s full month name.
%c 	Locale’s appropriate date and time representation.
%d 	Day of the month as a decimal number [01,31].
%f 	Microsecond as a decimal number [0,999999], zero-padded on the left
%H 	Hour (24-hour clock) as a decimal number [00,23].
%I 	Hour (12-hour clock) as a decimal number [01,12].
%j 	Day of the year as a decimal number [001,366].
%m 	Month as a decimal number [01,12].
%M 	Minute as a decimal number [00,59].
%p 	Locale’s equivalent of either AM or PM.
%S 	Second as a decimal number [00,61].
%U 	Week number (Sunday first weekday) as a decimal number [00,53].
%w 	Weekday as a decimal number [0(Sunday),6]. 	4
%W 	Week number (Monday first weekday) as a decimal number [00,53].
%x 	Locale’s appropriate date representation.
%X 	Locale’s appropriate time representation.
%y 	Year without century as a decimal number [00,99].
%Y 	Year with century as a decimal number.
%z 	UTC offset in the form +HHMM or -HHMM.
%Z 	Time zone name.
%% 	A literal '%' character.""")


class TextEditor(wx.Panel):
    """Editor widget for text objects

    The editor provides a taxt ctrl, a font button and a color chooser

    """

    style_wx2mpl = {
        wx.FONTSTYLE_ITALIC: "italic",
        wx.FONTSTYLE_NORMAL: "normal",
        wx.FONTSTYLE_SLANT: "oblique",
    }

    style_mpl2wx = dict((v, k) for k, v in style_wx2mpl.iteritems())

    weight_wx2mpl = {
        wx.FONTWEIGHT_BOLD: "bold",
        wx.FONTWEIGHT_NORMAL: "normal",
        wx.FONTWEIGHT_LIGHT: "light",
    }

    weight_mpl2wx = dict((v, k) for k, v in weight_wx2mpl.iteritems())

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.textctrl = wx.TextCtrl(self, -1)
        self.fontbutton = wx.Button(self, -1, label=u"\u2131", size=(24, 24))
        self.colorselect = csel.ColourSelect(self, -1, size=(24, 24))

        self.value = u""

        self.chosen_font = None

        self.font_face = None
        self.font_size = None
        self.font_style = None
        self.font_weight = None
        self.color = wx.BLACK

        self.__bindings()
        self.__do_layout()

    def __bindings(self):
        """Binds events to handlers"""

        self.textctrl.Bind(wx.EVT_TEXT, self.OnText)
        self.fontbutton.Bind(wx.EVT_BUTTON, self.OnFont)
        self.Bind(csel.EVT_COLOURSELECT, self.OnColor)

    def __do_layout(self):
        grid_sizer = wx.FlexGridSizer(1, 3, 0, 0)

        grid_sizer.Add(self.textctrl, 1, wx.ALL | wx.EXPAND, 0)
        grid_sizer.Add(self.fontbutton, 1, wx.ALL | wx.EXPAND, 0)
        grid_sizer.Add(self.colorselect, 1, wx.ALL | wx.EXPAND, 0)

        grid_sizer.AddGrowableCol(0)

        self.SetSizer(grid_sizer)

        self.fontbutton.SetToolTip(wx.ToolTip(_("Text font")))
        self.colorselect.SetToolTip(wx.ToolTip(_("Text color")))

        self.Layout()

    def get_code(self):
        """Returns code representation of value of widget"""

        return self.textctrl.GetValue()

    def get_kwargs(self):
        """Return kwargs dict for text"""

        kwargs = {}

        if self.font_face:
            kwargs["fontname"] = repr(self.font_face)
        if self.font_size:
            kwargs["fontsize"] = repr(self.font_size)
        if self.font_style in self.style_wx2mpl:
            kwargs["fontstyle"] = repr(self.style_wx2mpl[self.font_style])
        if self.font_weight in self.weight_wx2mpl:
            kwargs["fontweight"] = repr(self.weight_wx2mpl[self.font_weight])

        kwargs["color"] = color2code(self.colorselect.GetValue())

        code = ", ".join(repr(key) + ": " + kwargs[key] for key in kwargs)

        code = "{" + code + "}"

        return code

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of widget value

        """

        self.textctrl.SetValue(code)

    def set_kwargs(self, code):
        """Sets widget from kwargs string

        Parameters
        ----------
        code: String
        \tCode representation of kwargs value

        """

        kwargs = {}

        kwarglist = list(parse_dict_strings(code[1:-1]))

        for kwarg, val in zip(kwarglist[::2], kwarglist[1::2]):
            kwargs[unquote_string(kwarg)] = val

        for key in kwargs:
            if key == "color":
                color = code2color(kwargs[key])
                self.colorselect.SetOwnForegroundColour(color)

            elif key == "fontname":
                self.font_face = unquote_string(kwargs[key])

                if self.chosen_font is None:
                    self.chosen_font = get_default_font()
                self.chosen_font.SetFaceName(self.font_face)

            elif key == "fontsize":
                if kwargs[key]:
                    self.font_size = int(kwargs[key])
                else:
                    self.font_size = get_default_font().GetPointSize()

                if self.chosen_font is None:
                    self.chosen_font = get_default_font()

                self.chosen_font.SetPointSize(self.font_size)

            elif key == "fontstyle":
                self.font_style = \
                    self.style_mpl2wx[unquote_string(kwargs[key])]

                if self.chosen_font is None:
                    self.chosen_font = get_default_font()

                self.chosen_font.SetStyle(self.font_style)

            elif key == "fontweight":
                self.font_weight = \
                    self.weight_mpl2wx[unquote_string(kwargs[key])]

                if self.chosen_font is None:
                    self.chosen_font = get_default_font()

                self.chosen_font.SetWeight(self.font_weight)

    # Handlers

    def OnText(self, event):
        """Text entry event handler"""

        # post_command_event(self, self.DrawChartMsg)

    def OnFont(self, event):
        """Check event handler"""

        font_data = wx.FontData()

        # Disable color chooser on Windows
        font_data.EnableEffects(False)

        if self.chosen_font:
            font_data.SetInitialFont(self.chosen_font)

        dlg = wx.FontDialog(self, font_data)

        if dlg.ShowModal() == wx.ID_OK:
            font_data = dlg.GetFontData()

            font = self.chosen_font = font_data.GetChosenFont()

            self.font_face = font.GetFaceName()
            self.font_size = font.GetPointSize()
            self.font_style = font.GetStyle()
            self.font_weight = font.GetWeight()

        dlg.Destroy()

        # post_command_event(self, self.DrawChartMsg)

    def OnColor(self, event):
        """Check event handler"""

        # post_command_event(self, self.DrawChartMsg)


class AxesAttributes(object):
    """Provides tooltips and attributes for matplotlib axes attributes"""

    tick_choice_labels = [_("Inside"), _("Outside"), _("Both")]
    tick_choice_params = ["in", "out", "inout"]

    tooltips = {
        "plot_label": _(u"String or anything printable with ‘%s’ conversion"),
        "plot_xdata": _(u"The data np.array for x\n"
                        u"Code must eval to 1D array."),
        "plot_ydata": _(u"The data np.array for y\n"
                        u"Code must eval to 1D array."),
        "plot_linewidth": _(u"The line width in points"),
        "plot_marker": _(u"The line marker"),
        "plot_markersize": _(u"The marker size in points"),
        "bar_label": _(u"String or anything printable with ‘%s’ conversion"),
        "bar_left": _(u"The x coordinates of the left sides of the bars"),
        "bar_height": _(u"The heights of the bars"),
        "bar_width": _(u"The widths of the bars"),
        "bar_bottom": _(u"The y coordinates of the bottom edges of the bars"),
        "boxplot_x": _(u"An array or a sequence of vectors"),
        "boxplot_widths":
            _(u"Either a scalar or a vector and sets the width"
              u" of each box\nThe default is 0.5, or\n0.15*(distance "
              u"between extreme positions)\nif that is smaller"),
        "boxplot_vert": _(u"If True then boxes are drawn vertical\n"
                          u"If False then boxes are drawn horizontal"),
        "boxplot_sym": _(u"The symbol for flier points\nEnter an empty string "
                         u"(‘’)\nif you don’t want to show fliers"),
        "boxplot_notch": _(u"False produces a rectangular box plot\n"
                           u"True produces a notched box plot"),
        "hist_label": _(u"String or anything printable with ‘%s’ conversion"),
        "hist_x":
            _(u"Histogram data series\nMultiple data sets can be provided "
              u"as a list or as a 2-D ndarray in which each column"
              u"is a dataset. Note that the ndarray form is transposed "
              u"relative to the list form."),
        "hist_bins": _(u"Either an integer number of bins or a bin sequence"),
        "hist_normed":
            _(u"If True then the first element is the counts normalized"
                u"to form a probability density, i.e., n/(len(x)*dbin)."),
        "hist_cumulative":
            _(u"If True then each bin gives the counts in that bin"
              u"\nplus all bins for smaller values."),
        "pie_x": _(u"Pie chart data\nThe fractional area of each wedge is give"
                   u"n by x/sum(x)\nThe wedges are plotted counterclockwise"),
        "pie_labels": _(u"Sequence of wedge label strings"),
        "pie_colors":
            _(u"Sequence of matplotlib color args through which the pie "
              u"cycles.\nSupported strings are:\n'b': blue\n'g': green\n"
              u"'r': red\n'c': cyan\n'm': magenta\n'y': yellow\n'k': "
              u"black\n'w': white\nGray shades can be given as a string"
              u"that encodes a float in the 0-1 range, e.g.: '0.75'. "
              u"You can also specify the color with an html hex string "
              u"as in: '#eeefff'. Finally, legal html names for colors, "
              u"such as 'red', 'burlywood' and 'chartreuse' are "
              u"supported."),
        "pie_startangle":
            _(u"Rotates the start of the pie chart by angle degrees "
              u"counterclockwise from the x-axis."),
        "pie_shadow": _(u"If True then a shadow beneath the pie is drawn"),
        "ann_s": _(u"Annotation text"),
        "ann_xy": _(u"Point that is annotated"),
        "ann_xycoords": _(u"String that indicates the coordinates of xy"),
        "ann_xytext": _(u"Location of annotation text"),
        "ann_textcoords":
            _(u"String that indicates the coordinates of xy text."),
        "contour_X": _(u"X coordinates of the surface"),
        "contour_Y": _(u"Y coordinates of the surface"),
        "contour_Z": _(u"Z coordinates of the surface (contour height)"),
        "contour_colors":
            _(u"If None, the colormap specified by cmap will be used.\n"
              u"If a string, like ‘r’ or ‘red’, all levels will be "
              u"plotted in this color.\nIf a tuple of matplotlib color "
              u"args (string, float, rgb, etc), different levels will "
              u"be plotted in different colors in the order"
              u" specified."),
        "contour_alpha": _(u"The alpha blending value"),
        "contour_linestyles": _(u"Contour line style"),
        "contour_linewidths": _(u"All contour levels will be plotted with this"
                                u" linewidth."),
        "contour_labels": _(u"Adds contour labels"),
        "contour_label_fontsize": _(u"Contour font label size in points"),
        "contour_hatches":
            _(u"A list of cross hatch patterns to use on the filled "
              u"areas. A hatch can be one of:\n"
              u"/   - diagonal hatching\n"
              u"\   - back diagonal\n"
              u"|   - vertical\n"
              u"-   - horizontal\n"
              u"+   - crossed\n"
              u"x   - crossed diagonal\n"
              u"o   - small circle\n"
              u"O   - large circle\n"
              u".   - dots\n"
              u"*   - stars\n"
              u"Letters can be combined, in which case all the "
              u"specified hatchings are done. If same letter repeats, "
              u"it increases the density of hatching of that pattern."),
        "sankey_flows":
            _(u"Array of flow values.\nBy convention, inputs are positive"
              u" and outputs are negative."),
        "sankey_orientations":
            _(u"List of orientations of the paths.\nValid values "
              u"are 1 (from/to the top), 0 (from/to the left or "
              u"right), or -1 (from/to the bottom).\nIf "
              u"orientations == 0, inputs will break in from the "
              u"left and outputs will break away to the right."),
        "sankey_labels":
            _(u"List of specifications of the labels for the flows.\n"
              u"Each value may be None (no labels), ‘’ (just label the "
              u"quantities), or a labeling string. If a single value is "
              u"provided, it will be applied to all flows. If an entry "
              u"is a non-empty string, then the quantity for the "
              u"corresponding flow will be shown below the string. "
              u"However, if the unit of the main diagram is None, then "
              u"quantities are never shown, regardless of the value of "
              u"this argument."),
        "sankey_unit":
            _(u"String representing the physical unit associated with "
              u"the flow quantities.\nIf unit is None, then none of the "
              u"quantities are labeled."),
        "sankey_format":
            _(u"A Python number formatting string to be used in "
              u"labeling the flow as a quantity (i.e., a number times a "
              u"unit, where the unit is given)"),
        "sankey_rotation": _(u"Angle of rotation of the diagram [deg]"),
        "sankey_gap":
            _(u"Space between paths that break in/break away to/from the "
              u"top or bottom."),
        "sankey_radius": _(u"Inner radius of the vertical paths"),
        "sankey_shoulder": _(u"Size of the shoulders of output arrows"),
        "sankey_offset": _(u"Text offset (from the dip or tip of the arrow)"),
        "sankey_head_angle":
            _(u"Angle of the arrow heads (and negative of the angle "
              u"of the tails) [deg]"),
        "sankey_edgecolor": _(u"Edge color of Sankey diagram"),
        "sankey_facecolor": _(u"Face color of Sankey diagram"),
        "title": _(u"The figure title"),
        "xlabel": _(u"The label for the x axis"),
        "xlim": _(u"The data limits for the x axis\nFormat: (xmin, xmax)"),
        "ylabel": _(u"The label for the y axis"),
        "ylim": _(u"The data limits for the y axis\nFormat: (ymin, ymax)"),
        "xdate_format": _(u"If non-empty then the x axis is displays dates.\n"
                          u"Enter an unquoted strftime() format string."
                          u"\n") + strftime_doc,
        "xtick_labels": _(u"Custom labels for the x axis."),
        "ytick_labels": _(u"Custom labels for the y axis."),
        "xtick_location":
            _("Puts ticks inside the axes, outside the axes, or both."),
        "ytick_location":
            _("Puts ticks inside the axes, outside the axes, or both."),
        "xtick_padding": _("Distance in points between tick and label."),
        "ytick_padding": _("Distance in points between tick and label."),
        "xtick_size": _("Tick label font size in points."),
        "ytick_size": _("Tick label font size in points."),

    }

    items = [
        (_("axes"), (),
         [
            (_("figure"), (),
             [
                (_("title"),
                 ("title", TextEditor, [-1], {"size": (198, 25)}), []),
                (_("Legend"),
                 ("legend", wx.CheckBox, [-1, ""], {"style": wx.ALIGN_RIGHT}),
                 []),
             ]),
            (_("x-axis"), (), [
                (_("label"), ("xlabel", TextEditor, [-1], {"size": (198, 25)}),
                 []),
                (_("limits"), ("xlim", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("late format"), ("xdate_format", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("x-axis ticks"), ("xticks", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("x-axis labels"), ("xtick_labels", TextEditor, [-1],
                 {"size": (198, 25)}), []),
                (_("Log. scale"),
                 ("xscale", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("x-axis grid"),
                 ("xgrid", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("x-axis ticks"), (), [
                     (_("size"), ("xtick_size", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("padding"), ("xtick_padding", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("location"), ("xtick_location", wx.Choice, [-1],
                      {"size": (150, 25), "choices": tick_choice_labels}),
                      []),
                     (_("secondary"), ("xtick_secondary", wx.CheckBox,
                      [-1, ""], {"style": wx.ALIGN_RIGHT | wx.CHK_3STATE |
                                 wx.CHK_ALLOW_3RD_STATE_FOR_USER}), []),
                 ]),
             ]),
            (_("y-axis"), (), [
                (_("label"), ("ylabel", TextEditor, [-1],
                 {"size": (198, 25)}), []),
                (_("limits"), ("ylim", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("y-axis ticks"), ("yticks", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("y-axis labels"), ("ytick_labels", TextEditor, [-1],
                 {"size": (198, 25)}), []),
                (_("Log. scale"),
                 ("yscale", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("y-axis grid"),
                 ("ygrid", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("y-axis ticks"), (), [
                     (_("size"), ("ytick_size", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("padding"), ("ytick_padding", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("location"), ("ytick_location", wx.Choice, [-1],
                      {"size": (150, 25), "choices": tick_choice_labels}),
                      []),
                     (_("Secondary"), ("ytick_secondary", wx.CheckBox,
                      [-1, ""], {"style": wx.ALIGN_RIGHT | wx.CHK_3STATE |
                                 wx.CHK_ALLOW_3RD_STATE_FOR_USER}), []),
                 ]),
             ]),
         ]),
    ]


class PlotAttributes(object):
    """Provides tooltips and attributes for matplotlib plot attributes"""

    tooltips = {
        "label": _(u"String or anything printable with ‘%s’ conversion"),
        "xdata": _(u"The data np.array for x\n"
                   u"Code must eval to 1D array."),
        "ydata": _(u"The data np.array for y\n"
                   u"Code must eval to 1D array."),
        "linewidth": _(u"The line width in points"),
        "marker": _(u"The line marker"),
        "markersize": _(u"The marker size in points"),
    }

    items = [
        (_("plot"), (), [
            (_("label"), ("label", TextEditor, [-1], {"size": (198, 25)}), []),
            (_("x"), ("xdata", TextEditor, [-1], {"size": (198, 25)}), []),
            (_("y"), ("ydata", TextEditor, [-1], {"size": (198, 25)}), []),
            (_("style"), ("linestyle", LineStyleComboBox, [-1],
                          {"size": (150, 25)}), []),
            (_("line"), (), [
                (_("width"), ("linewidth", IntCtrl, [-1, 1],
                              {"size": (198, 25)}), []),
                (_("color"), ("color", ColourSelect, [-1, "", (0, 0, 0)], {}),
                 []),
                (_("style"), ("marker", MarkerStyleComboBox, [-1],
                              {"size": (198, 25)}), []),
            ]),
            (_("marker"), (), [
                (_("size"), ("markersize", IntCtrl, [-1, 5],
                             {"size": (198, 25)}), []),
                (_("face color"), ("markerfacecolor", ColourSelect,
                                   [-1, "", (0, 0, 0)], {}), []),
                (_("edge color"), ("markeredgecolor", ColourSelect,
                                   [-1, "", (0, 0, 0)], {}), []),
            ]),
        ])
    ]


class ChartTree(htl.HyperTreeList):
    """Tree widget for chart attributes"""

    def __init__(self, parent, *args, **kwargs):

        htl.HyperTreeList.__init__(
            self, parent, *args,
            agwStyle=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT |
            wx.TR_HAS_VARIABLE_ROW_HEIGHT, **kwargs)

        self.parent = parent

        self.items = {}
        self._init_items()

        self.tooltips = {}
        self._init_tooltips()

        # Create columns
        self.AddColumn("Attributes")
        self.AddColumn("Values")
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 175)
        self.SetColumnWidth(1, 200)

        # Add a root node to it
        self.root = self.AddRoot(_("Chart"))

        # Add axes content
        self.add_chart("axes")

    def _init_items(self):
        """Initializes self.items"""

        self.items["axes"] = AxesAttributes.items
        self.items["plot"] = PlotAttributes.items

    def _init_tooltips(self):
        """Initializes self.tooltips"""

        self.tooltips.update(AxesAttributes.tooltips)
        self.tooltips.update(PlotAttributes.tooltips)

    def add_chart(self, chart_type):
        """Adds axes or chart type to tree"""

        self.add_items(self.root, self.items[chart_type], self.tooltips)

    def add_items(self, node, items, tooltips):
        """Adds items to tree"""

        # Create an image list to add icons next to an item
        il = wx.ImageList(16, 16)
        fldridx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,
                                                  wx.ART_OTHER, (16, 16)))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,
                                                      wx.ART_OTHER, (16, 16)))
        fileidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,
                                                  wx.ART_OTHER, (16, 16)))
        self.SetImageList(il)

        for label, widget_info, children in items:
            if widget_info:
                name, widget_cls, args, kwargs = widget_info
                widget = widget_cls(self, *args, **kwargs)

                widget.Bind(wx.EVT_TEXT, self.OnText)

                try:
                    widget.SetToolTip(wx.ToolTip(tooltips[name]))
                except KeyError:
                    pass

                child = self.AppendItem(node, label)

                widget.object_type = "axes"
                widget.treeitem = child
                widget.name = name

                self.SetItemWindow(child, widget, 1)
                self.SetItemImage(child, fileidx, wx.TreeItemIcon_Normal)

            else:
                child = self.AppendItem(node, label)

                self.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
                self.SetItemImage(child, fldropenidx,
                                  wx.TreeItemIcon_Expanded)

            self.ExpandAll()
            self.add_items(child, children, tooltips)

    def walk_items(self, item):
        """Generator that walks items depth first"""

        yield item

        for child in item.GetChildren():
            for gc in self.walk_items(child):
                yield gc

    def get_figure(self, code):
        """Returns figure from executing code in grid

        Returns an empty matplotlib figure if code does not eval to a
        matplotlib figure instance.

        Parameters
        ----------
        code: Unicode
        \tUnicode string which contains Python code that should yield a figure

        """

        # Caching for fast response if there are no changes
        if code == self.figure_code_old and self.figure_cache:
            return self.figure_cache

        self.figure_code_old = code

        # key is the current cursor cell of the grid
        key = self.grid.actions.cursor
        cell_result = self.grid.code_array._eval_cell(key, code)

        # If cell_result is matplotlib figure
        if isinstance(cell_result, Figure):
            # Return it
            self.figure_cache = cell_result
            return cell_result

        else:
            # Otherwise return empty figure
            self.figure_cache = charts.ChartFigure()

        return self.figure_cache

    # Tuple keys have to be put in parentheses
    tuple_keys = ["xdata", "ydata", "left", "height", "width", "bottom",
                  "xlim", "ylim", "x", "labels", "colors", "xy", "xytext",
                  "title", "xlabel", "ylabel", "label", "X", "Y", "Z",
                  "hatches", "flows", "orientations", "labels"]

    # String keys need to be put in "
    string_keys = ["type", "linestyle", "marker", "shadow", "vert", "xgrid",
                   "ygrid", "notch", "sym", "normed", "cumulative",
                   "xdate_format", "xycoords", "textcoords", "linestyles",
                   "contour_labels", "contour_fill", "format", "unit"]

    # Keys, which have to be None if empty
    empty_none_keys = ["colors", "color"]

    def set_code(self, code):
        """Update widgets from code"""

        # Get attributes from code

        attributes = []
        strip = lambda s: s.strip('u').strip("'").strip('"')
        for attr_dict in parse_dict_strings(unicode(code).strip()[19:-1]):
            attrs = list(strip(s) for s in parse_dict_strings(attr_dict[1:-1]))
            attributes.append(dict(zip(attrs[::2], attrs[1::2])))

        if not attributes:
            return

        # Set widgets from attributes
        # ---------------------------

        # Figure attributes
        figure_attributes = attributes[0]

        for key, widget in self.figure_attributes_panel:
            try:
                obj = figure_attributes[key]
                kwargs_key = key + "_kwargs"
                if kwargs_key in figure_attributes:
                    widget.set_kwargs(figure_attributes[kwargs_key])

            except KeyError:
                obj = ""

            widget.code = charts.object2code(key, obj)

        # Series attributes
        self.all_series_panel.update(attributes[1:])

    def get_parents(self, item):
        """Returns list of parents including item starting with item"""

        if item == self.root:
            return []

        parent = item.GetParent()

        return self.get_parents(parent) + [parent]

    def get_code(self):
        """Returns code that generates figure from widgets"""

        attr_dict = {}

        for item in self.walk_items(self.root):

            keylist = [parent.GetText() for parent in self.get_parents(item)]
            keylist += [item.GetText()]
            key = tuple(keylist)

            value = None
            window = self.GetItemWindow(item, 1)
            if window:
                try:
                    value = window.GetText()
                except AttributeError:
                    try:
                        value = window.GetValue()
                    except AttributeError:
                        try:
                            value = [window.get_code(), window.get_kwargs()]
                        except AttributeError:
                            pass

            if key and value:
                attr_dict[key] = value
        print attr_dict

#        def dict2str(attr_dict):
#            """Returns string with dict content with values as code
#
#            Code means that string identifiers are removed
#
#            """
#
#            result = u"{"
#
#            for key in attr_dict:
#                code = attr_dict[key]
#
#                if key in self.string_keys:
#                    code = repr(code)
#
#                elif code and key in self.tuple_keys and \
#                     not (code[0] in ["[", "("] and code[-1] in ["]", ")"]):
#
#                    code = "(" + code + ")"
#
#                elif key in ["xscale", "yscale"]:
#                    if code:
#                        code = '"log"'
#                    else:
#                        code = '"linear"'
#
#                elif key in ["legend"]:
#                    if code:
#                        code = '1'
#                    else:
#                        code = '0'
#
#                elif key in ["xtick_params"]:
#                    code = '"x"'
#
#                elif key in ["ytick_params"]:
#                    code = '"y"'
#
#                if not code:
#                    if key in self.empty_none_keys:
#                        code = "None"
#                    else:
#                        code = 'u""'
#
#                result += repr(key) + ": " + code + ", "
#
#            result = result[:-2] + u"}"
#
#            return result
#
#        # cls_name inludes full class name incl. charts
#        cls_name = "charts." + charts.ChartFigure.__name__
#
#        attr_dicts = []
#
#        # Figure attributes
#        attr_dict = {}
#        # figure_attributes is a dict key2code
#        for key, widget in self.figure_attributes_panel:
#            if key == "type":
#                attr_dict[key] = widget
#            else:
#                attr_dict[key] = widget.code
#                try:
#                    attr_dict[key+"_kwargs"] = widget.get_kwargs()
#                except AttributeError:
#                    pass
#
#        attr_dicts.append(attr_dict)
#
#        # Series_attributes is a list of dicts key2code
#        for series_panel in self.all_series_panel:
#            attr_dict = {}
#            for key, widget in series_panel:
#                if key == "type":
#                    attr_dict[key] = widget
#                else:
#                    attr_dict[key] = widget.code
#
#            attr_dicts.append(attr_dict)
#
#        code = cls_name + "("
#
#        for attr_dict in attr_dicts:
#            code += dict2str(attr_dict) + ", "
#
#        code = code[:-2] + ")"

#        return code

    # Handlers

    def OnText(self, event):
        print self.get_code()

        self.parent.parent.figure_panel.update(self.parent.parent.figure)


class FigurePanel(wx.Panel):
    """Panel that draws a matplotlib figure_canvas"""

    def __init__(self, parent):

        self.parent = parent

        wx.Panel.__init__(self, parent)
        self.__do_layout()

    def __do_layout(self):
        self.main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        self.main_sizer.AddGrowableRow(0)
        self.main_sizer.AddGrowableCol(0)

        self.SetSizer(self.main_sizer)

        self.Layout()

    def _get_figure_canvas(self, figure):
        """Returns figure canvas"""

        return FigureCanvasWxAgg(self, -1, figure)

    def update(self, figure):
        """Updates figure on data change

        Parameters
        ----------
        * figure: matplotlib.figure.Figure
        \tMatplotlib figure object that is displayed in self

        """

        if hasattr(self, "figure_canvas"):
            self.figure_canvas.Destroy()

        self.figure_canvas = self._get_figure_canvas(figure)

        self.figure_canvas.mpl_connect('button_press_event', self.onclick)
        self.figure_canvas.mpl_connect('pick_event', self.onpick)

        self.figure_canvas.SetSize(self.GetSize())
        figure.subplots_adjust()

        self.main_sizer.Add(self.figure_canvas, 1,
                            wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.Layout()
        self.figure_canvas.draw()

    def onclick(self, event):
        return
        print 'button={}, x={}, y={}, xdata={}, ydata={}'.format(
            event.button, event.x, event.y, event.xdata, event.ydata)

#        if not event.inaxes:
#            self.parent.parent.tree.SelectItem(item)

    def onpick(self, event):
        """Matplotlib pick event handler"""

        # TODO: Decouple via post event
        if hasattr(event.artist, "name"):
            name = event.artist.name
            #item = self.parent.parent.tree.name2widget[name]
            #self.parent.parent.tree.SelectItem(item)


class ChartDialog(wx.Dialog):
    """Chart dialog frontend to matplotlib"""

    chart_types = [
        "plot"
    ]

    def __init__(self, parent, *args, **kwargs):
        wx.Dialog.__init__(self, parent, -1, _("Insert chart"), *args,
                           size=(900, 700), style=wx.RESIZE_BORDER, **kwargs)

        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)
        self.splitter.parent = self

        # Create a CustomTreeCtrl instance
        self.tree = ChartTree(self.splitter, style=wx.BORDER_SUNKEN)
        self.figure_panel = FigurePanel(self.splitter)

        # Dummy figure
        self.figure = Figure(facecolor='white')
        ax = self.figure.add_subplot(111)
        ax.xaxis.set_picker(5)
        ax.xaxis.name = "xaxis"
        ax.yaxis.set_picker(5)
        ax.yaxis.name = "yaxis"
        plt = ax.plot([(x/10.0)**2 for x in xrange(1000)], picker=5)
        plt[-1].name = "test"
        self.figure_panel.update(self.figure)

        # Split Window
        self.splitter.SplitVertically(self.tree, self.figure_panel)
        self.splitter.SetMinimumPaneSize(10)
        self.splitter.SetSashPosition(400)

        # Buttons
        self.button_add = wx.Button(self, wx.ID_ADD)
        self.button_remove = wx.Button(self, wx.ID_REMOVE)
        self.button_cancel = wx.Button(self, wx.ID_CANCEL)
        self.button_ok = wx.Button(self, wx.ID_OK)

        self.button_add.Bind(wx.EVT_BUTTON, self.OnAdd)

        self._layout()

    def _layout(self):
        """Sizer layout"""

        left_sizer = wx.FlexGridSizer(cols=1)
        left_button_sizer = wx.FlexGridSizer(cols=5)

        left_sizer.Add(self.splitter, 0, wx.EXPAND)
        left_sizer.Add(left_button_sizer, 0, wx.EXPAND)

        left_button_sizer.Add(self.button_add, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_remove, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(wx.Panel(self,  -1), 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_cancel, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_ok, 1, wx.EXPAND | wx.ALL, 4)

        left_sizer.AddGrowableRow(0)
        left_sizer.AddGrowableCol(0)

        left_button_sizer.AddGrowableCol(2)

        self.SetSizer(left_sizer)
        self.Layout()

    def add_chart(self, chart_type):
        """Adds chart to figure after current position in the tree"""

        self.tree.add_chart(chart_type)

    # Event handlers

    def OnAdd(self, event):
        """Add button event handler"""

        dlg = wx.SingleChoiceDialog(self, _('Add chart to figure'),
                                    _('Select chart type'),
                                    self.chart_types,
                                    wx.CHOICEDLG_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.add_chart(dlg.GetStringSelection())

        dlg.Destroy()


def main():
    """Create a chart_dialog2 and return output on OK"""

    app = wx.App(0)
    chart_dialog = ChartDialog(None)
    app.SetTopWindow(chart_dialog)
    chart_dialog.CenterOnScreen()
    val = chart_dialog.ShowModal()

    chart_dialog.Destroy()

    return val

if __name__ == "__main__":
    print main()
