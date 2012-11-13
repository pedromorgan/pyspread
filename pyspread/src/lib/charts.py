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
charts
======

Provides matplotlib figure that are chart templates

Provides
--------

* ChartFigure: Main chart class

"""

import i18n
import types

import wx
import wx.lib.colourselect as csel
from wx.lib.intctrl import IntCtrl
from matplotlib.figure import Figure

from gui._widgets import PenWidthComboBox, LineStyleComboBox
from gui._widgets import MarkerStyleComboBox

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


int_validator = lambda x: isinstance(x, types.IntType)
color_validator = lambda x: isinstance(x, types.IntType) and len(x) == 3
linestyle_validator = lambda x: x in [s[1] for s in LineStyleComboBox.styles]
markerstyle_validator = lambda x: x in [s[1]
                            for s in MarkerStyleComboBox.styles]

charts = {
    "plot": {
        "defaults": {
            "xdata": u"",
            "ydata": u"",
            "linestyle": u"'-'",
            "linewidth": u"1",
            "color": u"(0, 0, 0)",
            "marker": u"''",
            "markersize": u"5",
            "markerfacecolor": u"(0, 0, 0)",
            "markeredgecolor": u"(0, 0, 0)",
        },
        "args": ["xdata", "ydata"],
        "labels": {
            "xdata": _("X"),
            "ydata": _("Y"),
            "linestyle": _("Style"),
            "linewidth": _("Width"),
            "color": _("Color"),
            "marker": _("Style"),
            "markersize": _("Size"),
            "markerfacecolor": _("Face"),
            "markeredgecolor": _("Edge"),
        },
        "boxes": [
            (_("Data"), "xdata", "ydata"),
            (_("Line"), "linestyle", "color", "linewidth"),
            (_("Marker"), "marker", "markersize", "markerfacecolor",
                          "markeredgecolor"),
        ],
        "widgets": {
            "xdata": (wx.TextCtrl,
                      {"tooltip":  _("Enter a list of X values (optional).")}),
            "ydata": (wx.TextCtrl,
                      {"tooltip":  _("Enter a list of Y values.")}),
            "linestyle": (LineStyleComboBox, {"size": (80, 25)}),
            "linewidth": (PenWidthComboBox,
                              {"choices": map(unicode, xrange(12)),
                               "style": wx.CB_READONLY, "size": (50, -1)}),
            "color": (csel.ColourSelect, {}),
            "marker": (MarkerStyleComboBox, {}),
            "markersize": (IntCtrl, {}),
            "markerfacecolor": (csel.ColourSelect, {"size": (80, 25)}),
            "markeredgecolor": (csel.ColourSelect, {"size": (80, 25)}),
        },
        "validators": {
            "xdata": iter,
            "ydata": iter,
            "linestyle": linestyle_validator,
            "linewidth": int_validator,
            "color": color_validator,
            "marker": markerstyle_validator,
            "markersize": int_validator,
            "markerfacecolor": color_validator,
            "markeredgecolor": color_validator,
        },
    },
    "bar": {
        "defaults": {
            "xdata": u"",
            "ydata": u"",
            "linestyle": u"'-'",
            "linewidth": u"1",
            "color": u"(0, 0, 0)",
            "marker": u"''",
            "markersize": u"5",
            "markerfacecolor": u"(0, 0, 0)",
            "markeredgecolor": u"(0, 0, 0)",
        },
        "args": ["xdata", "ydata"],
        "labels": {
            "xdata": _("X"),
            "ydata": _("Y"),
            "linestyle": _("Style"),
            "linewidth": _("Width"),
            "color": _("Color"),
            "marker": _("Style"),
            "markersize": _("Size"),
            "markerfacecolor": _("Face"),
            "markeredgecolor": _("Edge"),
        },
        "boxes": [
            (_("Data"), "xdata", "ydata"),
            (_("Line"), "linestyle", "color", "linewidth"),
            (_("Marker"), "marker", "markersize", "markerfacecolor",
                          "markeredgecolor"),
        ],
        "widgets": {
            "xdata": (wx.TextCtrl,
                      {"tooltip":  _("Enter a list of X values (optional).")}),
            "ydata": (wx.TextCtrl,
                      {"tooltip":  _("Enter a list of Y values.")}),
            "linestyle": (LineStyleComboBox, {"size": (80, 25)}),
            "linewidth": (PenWidthComboBox,
                              {"choices": map(unicode, xrange(12)),
                               "style": wx.CB_READONLY, "size": (50, -1)}),
            "color": (csel.ColourSelect, {}),
            "marker": (MarkerStyleComboBox, {}),
            "markersize": (IntCtrl, {}),
            "markerfacecolor": (csel.ColourSelect, {"size": (80, 25)}),
            "markeredgecolor": (csel.ColourSelect, {"size": (80, 25)}),
        },
        "validators": {
            "xdata": iter,
            "ydata": iter,
            "linestyle": linestyle_validator,
            "linewidth": int_validator,
            "color": color_validator,
            "marker": markerstyle_validator,
            "markersize": int_validator,
            "markerfacecolor": color_validator,
            "markeredgecolor": color_validator,
        },
    },
}


class ChartFigure(Figure):
    """Chart figure class with drawing method"""

    plot_type_fixed_attrs = {
        "plot": ["ydata"],
        "bar": ["xdata", "ydata"],
    }
    plot_type_kwd_attrs = {
        "plot": ["linestyle"],
        "bar": [],
    }

    def __init__(self, *chart_data):

        Figure.__init__(self, (5.0, 4.0), facecolor="white")

        self.chart_data = chart_data
        self.__axes = self.add_subplot(111)
        self.draw_chart()

    def _setup_axes(self, axes_data):
        """Sets up axes for drawing chart"""

        self.__axes.clear()

        if "xlabel" in axes_data:
            if axes_data["xlabel"]:
                self.__axes.set_xlabel(axes_data["xlabel"])

        if "ylabel" in axes_data:
            if axes_data["ylabel"]:
                self.__axes.set_ylabel(axes_data["ylabel"])

    def draw_chart(self):
        """Plots chart from self.chart_data.clear"""

        if not hasattr(self, "chart_data"):
            return

        # The first element is always aaxes data
        self._setup_axes(self.chart_data[0])

        for series in self.chart_data[1:]:
            # Extract chart type
            chart_type_string = series.pop("type")

            # Check xdata length
            if "xdata" in series and \
               len(series["xdata"]) != len(series["ydata"]):
                # Wrong length --> ignore xdata
                series.pop("xdata")
            else:
                series["xdata"] = tuple(series["xdata"])

            fixed_attrs = []
            for attr in self.plot_type_fixed_attrs[chart_type_string]:
                # Remove attr if it is a fixed (non-kwd) attr
                # If a fixed attr is missing, insert a dummy

                # TODO: Move kwds into extra classes
                try:
                    fixed_attrs.append(tuple(series.pop(attr)))
                except KeyError:
                    fixed_attrs.append(())

            # Remove unneeded kwd attrs
            attrs = self.plot_type_kwd_attrs[chart_type_string]
            for attr in series.keys():
                if attr not in attrs:
                    series.pop(attr)

            if all(fixed_attrs):

                # Draw series to axes
                chart_method = getattr(self.__axes, chart_type_string)
                chart_method(*fixed_attrs, **series)