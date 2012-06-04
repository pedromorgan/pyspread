#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Martin Manns
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

charts
======

Provides different types of data charts

"""

from cStringIO import StringIO

import matplotlib
import wx


def fig2bmp(fig, width, height):
    """Returns wx.Bitmap from matplotlib chart

    Parameters
    ----------
    fig: Object
    \tMatplotlib figure
    width: Integer
    \tImage width in pixels
    height: Integer
    \tImage height in pixels

    """

    matplotlib.use('Agg')
    png_stream = StringIO()
    fig.savefig(png_stream, format='png')

    return wx.BitmapFromImage(wx.ImageFromStream(png_stream))


class Chart(object):
    """Chart base class"""

    def __init__(self, x, *ys):
        self.figure = self._get_figure(x, *ys)

    def get_bmp(self, width, height):
        """Returns wx.Bitmap of chart"""

        return fig2bmp(self.figure, width, height)


class LineChart(Chart):
    """Line chart

    Parameters
    ----------
    series: numpy.array
    \tSeries that are shown in chart

    """

    def _get_figure(self, x, *ys):
        """Returns figure of line chart"""

        series = ((x, y, "-") for y in ys)

        figure = matplotlib.pyplot.figure()
        axis = figure.add_subplot(111)
        args = []

        for line in series:
            args.append(*line)
        axis.plot(args)

        return figure