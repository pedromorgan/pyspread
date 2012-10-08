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

from matplotlib.figure import Figure


class ChartFigure(Figure):
    """Chart figure class with drawing method"""

    def __init__(self, *chart_data):
        self.chart_data = chart_data
        Figure.__init__(self, (5.0, 4.0), facecolor="white")

        self.__axes = self.add_subplot(111)
        self.draw_chart()

    def draw_chart(self):
        """Plots chart from self.chart_data.clear"""
        self.__axes.clear()

        for series in self.chart_data:
            # xdata and ydata is extracted and handled separately
            try:
                ydata = series.pop("ydata")

            except KeyError:
                ydata = []

            # Check xdata length
            if "xdata" in series and len(series["xdata"]) != len(ydata):
                # Wrong length --> ignore xdata
                series.pop("xdata")
            if ydata:

                # Draw series to axes
                self.__axes.plot(ydata, **series)