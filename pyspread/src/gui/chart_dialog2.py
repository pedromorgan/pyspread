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


from matplotlib.pyplot import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

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

    axes_tick_choice_labels = [_("Inside"), _("Outside"), _("Both")]
    axes_tick_choice_params = ["in", "out", "inout"]

    axes_tooltips = {
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

    axes_items = [
        (_("Axes"), (),
         [
            (_("Figure"), (),
             [
                (_("Title"),
                 ("title", TextEditor, [-1], {"size": (198, 25)}), []),
                (_("Legend"),
                 ("legend", wx.CheckBox, [-1, ""], {"style": wx.ALIGN_RIGHT}),
                 []),
             ]),
            (_("X-Axis"), (), [
                (_("Label"), ("xlabel", TextEditor, [-1], {"size": (198, 25)}),
                 []),
                (_("Limits"), ("xlim", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("Date format"), ("xdate_format", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("X-axis ticks"), ("xticks", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("X-axis labels"), ("xtick_labels", TextEditor, [-1],
                 {"size": (198, 25)}), []),
                (_("Log. scale"),
                 ("xscale", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("X-axis grid"),
                 ("xgrid", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("X-axis ticks"), (), [
                     (_("Size"), ("xtick_size", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("Padding"), ("xtick_padding", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("Location"), ("xtick_location", wx.Choice, [-1],
                      {"size": (150, 25), "choices": axes_tick_choice_labels}),
                      []),
                     (_("Secondary"), ("xtick_secondary", wx.CheckBox,
                      [-1, ""], {"style": wx.ALIGN_RIGHT | wx.CHK_3STATE |
                                 wx.CHK_ALLOW_3RD_STATE_FOR_USER}), []),
                 ]),
             ]),
            (_("Y-Axis"), (), [
                (_("Label"), ("ylabel", TextEditor, [-1],
                 {"size": (198, 25)}), []),
                (_("Limits"), ("ylim", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("Y-axis ticks"), ("yticks", wx.TextCtrl, [-1],
                 {"size": (150, 25)}), []),
                (_("Y-axis labels"), ("ytick_labels", TextEditor, [-1],
                 {"size": (198, 25)}), []),
                (_("Log. scale"),
                 ("yscale", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("Y-axis grid"),
                 ("ygrid", wx.CheckBox, [-1, ""],
                  {"style": wx.ALIGN_RIGHT}), []),
                (_("Y-axis ticks"), (), [
                     (_("Size"), ("ytick_size", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("Padding"), ("ytick_padding", wx.TextCtrl, [-1],
                      {"size": (150, 25)}), []),
                     (_("Location"), ("ytick_location", wx.Choice, [-1],
                      {"size": (150, 25), "choices": axes_tick_choice_labels}),
                      []),
                     (_("Secondary"), ("ytick_secondary", wx.CheckBox,
                      [-1, ""], {"style": wx.ALIGN_RIGHT | wx.CHK_3STATE |
                                 wx.CHK_ALLOW_3RD_STATE_FOR_USER}), []),
                 ]),
             ]),
         ]),
    ]


class ChartTree(htl.HyperTreeList, AxesAttributes):
    """Tree widget for chart attributes"""

    def __init__(self, parent, *args, **kwargs):

        htl.HyperTreeList.__init__(
            self, parent, *args,
            agwStyle=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT |
            wx.TR_HAS_VARIABLE_ROW_HEIGHT, **kwargs)

        # Mapping of field names to widget instances
        self.label2widget = {}

        # Create columns
        self.AddColumn("Attributes")
        self.AddColumn("Values")
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 175)
        self.SetColumnWidth(1, 200)

        # Add a root node to it
        root = self.AddRoot(_("Chart"))
        self.add_items(root, self.axes_items, self.axes_tooltips)
        self.ExpandAll()

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
                self.label2widget[label] = widget

                try:
                    widget.SetToolTip(wx.ToolTip(tooltips[name]))
                except KeyError:
                    pass

                child = self.AppendItem(node, label)
                self.SetItemWindow(child, widget, 1)
                self.SetItemImage(child, fileidx, wx.TreeItemIcon_Normal)

            else:
                child = self.AppendItem(node, label)
                self.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
                self.SetItemImage(child, fldropenidx,
                                  wx.TreeItemIcon_Expanded)

            self.add_items(child, children, tooltips)


class FigurePanel(wx.Panel):
    """Panel that draws a matplotlib figure_canvas"""

    def __init__(self, parent):

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
        print 'button={}, x={}, y={}, xdata={}, ydata={}'.format(
            event.button, event.x, event.y, event.xdata, event.ydata)
        print 'inaxes={}'.format(event.inaxes)

    def onpick(self, event):
        print "artist={}, ind={}".format(event.artist, event.ind)

class ChartDialog(wx.Dialog):
    """Chart dialog frontend to matplotlib"""

    def __init__(self, parent, *args, **kwargs):
        wx.Dialog.__init__(self, parent, -1, _("Insert chart"), *args,
                           size=(900, 700), **kwargs)

        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)

        # Create a CustomTreeCtrl instance
        self.tree = ChartTree(self.splitter, style=wx.BORDER_SUNKEN)
        self.figure_panel = FigurePanel(self.splitter)

        # Dummy figure
        figure = Figure(facecolor='white')
        ax = figure.add_subplot(111)
        ax.plot([(x/10.0)**2 for x in xrange(1000)], picker=5)
        self.figure_panel.update(figure)

        # Split Window
        self.splitter.SplitVertically(self.tree, self.figure_panel)
        self.splitter.SetMinimumPaneSize(10)
        self.splitter.SetSashPosition(400)

        # Buttons
        self.button_add = wx.Button(self, wx.ID_ADD)
        self.button_remove = wx.Button(self, wx.ID_REMOVE)
        self.button_up = wx.Button(self, wx.ID_UP)
        self.button_down = wx.Button(self, wx.ID_DOWN)
        self.button_cancel = wx.Button(self, wx.ID_CANCEL)
        self.button_ok = wx.Button(self, wx.ID_OK)

        self._layout()

    def _layout(self):
        """Sizer layout"""

        left_sizer = wx.FlexGridSizer(cols=1)
        left_button_sizer = wx.FlexGridSizer(cols=7)

        left_sizer.Add(self.splitter, 0, wx.EXPAND)
        left_sizer.Add(left_button_sizer, 0, wx.EXPAND)

        left_button_sizer.Add(self.button_add, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_remove, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_up, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_down, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(wx.Panel(self,  -1), 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_cancel, 1, wx.EXPAND | wx.ALL, 4)
        left_button_sizer.Add(self.button_ok, 1, wx.EXPAND | wx.ALL, 4)

        left_sizer.AddGrowableRow(0)
        left_sizer.AddGrowableCol(0)

        left_button_sizer.AddGrowableCol(4)

        self.SetSizer(left_sizer)
        self.Layout()


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
