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

* PlotFigure: Plot figure class

"""

from matplotlib.figure import Figure


class PlotFigure(Figure):
    """Plot figure class with drawing method"""

    def __init__(self, **chart_data):
        self.chart_data = chart_data
        Figure.__init__(self, (5.0, 4.0), facecolor="white")
        self.__axes = self.add_subplot(111)
        self.draw_chart()

    def draw_chart(self):
        # Update chart data
        for key in self.chart_data:
            setattr(self, key, self.chart_data[key])

        # Clear the axes and redraw the plot anew

        self.__axes.clear()

        if hasattr(self, "x_data") and len(self.x_data) == len(self.y1_data):
            self.__axes.plot(self.y1_data, linewidth=self.line_width,
                             xdata=self.x_data, color=self.line_color)
        else:
            self.__axes.plot(self.y1_data, linewidth=self.line_width,
                             color=self.line_color)