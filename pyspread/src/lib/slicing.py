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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
slicing.py
==========

"""


def slice2range(slc, length):
    """Converts slice to start stop step values for xrange

    slc: slice
    \tThe slice to be converted
    shape: Integer
    \tLength of the target vector

    """

    start = slc.start if slc.start is not None else 0
    stop = slc.stop if slc.stop is not None else length
    step = slc.step if slc.step is not None else 1
    if step < 0:
        start, stop = stop, start

    return start, stop, step
