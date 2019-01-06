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

images
======

Functions for converting between QPixmap and numoy array

"""

from copy import deepcopy
import numpy

from PyQt5.QtGui import QImage


def ndarray2qimage(array):
    """Converts a numpy ndarray to a QImage with Format_ARGB32_Premultiplied

    Parameters
    ----------
     * ndarray: numpy.ndarray with dtype uint32
    \t3D numpy ndarray that contains color values as A, R, G, B

    """

    assert isinstance(array, numpy.ndarray), "array must be a numpy.ndarray"
    assert len(array.shape) == 3 and array.shape[2] == 4, \
        "array must have the shape (width, height, 4)"

    height, width, depth = array.shape

    buffer = (array[:, :, 0] << 24 | array[:, :, 1] << 16
              | array[:, :, 2] << 8 | array[:, :, 3])

    qimage = QImage(buffer, width, height, QImage.Format_ARGB32)
    return qimage.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)


def qimage_to_array(qimage):
    """Returns a numpy array from a QImage.

    The format of the numpy array elements follows RGBA

    """

    assert isinstance(qimage, QImage), "img must be a QtGui.QImage object"

    img = qimage.convertToFormat(QImage.Format.Format_ARGB32)

    height, width, channels = img.height(), img.width(), 4

    string = img.bits().asstring(width * height * channels)
    array = numpy.fromstring(string, dtype=numpy.uint8)
    return array.reshape((height, width, channels))
