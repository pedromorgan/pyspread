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

import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot


class Chart(matplotlib.pyplot.Figure):
    """Chart base class"""

    def __init__(self, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs
        matplotlib.pyplot.Figure.__init__(self)
        self._set_figure()

    def _set_figure(self):
        """Returns figure of chart.

        Shall be overloaded from subclasses

        """

        raise NotImplementedError("Use child class.")


class Plot(Chart):
    def _set_figure(self):
        """Returns figure of line chart."""

        series = ((x ** 1.5, x ** 2) for x in xrange(100))

        axis = self.add_subplot(111)
        args = []

        for line in series:
            args.append(line)
        axis.plot(args)


def get_chart_cls(name):
    """Chart class factory"""

    name2cls = {"plot": Plot}
    return name2cls[name]


def parse_chart_code(code):
    """Parsed chart code to class and parameters"""

    if code[:6] != "chart(":
        raise ValueError("No chart code")


def chart(chart_type, *args, **kwargs):
    """Chart caller"""

    return get_chart_cls(chart_type)(*args, **kwargs)