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

import copy
import numpy as np

def np2qpixmap(np_img):
    frame = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
    img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
    return QtGui.QPixmap.fromImage(img)


a = np.random.randint(0,256,size=(100,100,3)).astype(np.uint32)
b = (255 << 24 | a[:,:,0] << 16 | a[:,:,1] << 8 | a[:,:,2]).flatten() # pack RGB values
b = (255 << 24 | a[:,:,0] << 16 | a[:,:,1] << 8 | a[:,:,2])
im = PySide.QtGui.QImage(b, 100, 100, PySide.QtGui.QImage.Format_RGB32)


Great solution! To make it work for me, I needed to make a small change and use PySide.QtGui.QImage.Format_ARGB32. The rest is the same. – P.R. Sep 26 '13 at 20:42
care to explain the b=... line, I don't get it at all... :s why 255, 24, 16, 8 ? I'm guessing it's related to 2^8, 2^4, 2^3 but what about 24? Also an explanation would be nice, thank you! – evan54 Jan 10 '15 at 2:08
@evan54, the red, green, and blue values are packed into the first 8 bytes, bytes 8-16, and bytes 16-24 respectively. The last 8 bytes are sometimes used for the alpha value. In this case, 255 is the maximum value for an 8 bit value which just says that all the colors should be visible (no transparency). – user545424 Jan 10 '15 at 19:17

def qt_image_to_array(img, share_memory=False):
    """ Creates a numpy array from a QImage.

        If share_memory is True, the numpy array and the QImage is shared.
        Be careful: make sure the numpy array is destroyed before the image,
        otherwise the array will point to unreserved memory!!
    """
    assert isinstance(img, QtGui.QImage), "img must be a QtGui.QImage object"
    assert img.format() == QtGui.QImage.Format.Format_RGB32, \
        "img format must be QImage.Format.Format_RGB32, got: {}".format(img.format())

    img_size = img.size()
    buffer = img.constBits()

    # Sanity check
    n_bits_buffer = len(buffer) * 8
    n_bits_image  = img_size.width() * img_size.height() * img.depth()
    assert n_bits_buffer == n_bits_image, \
        "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image)

    assert img.depth() == 32, "unexpected image depth: {}".format(img.depth())

    # Note the different width height parameter order!
    arr = np.ndarray(shape  = (img_size.height(), img_size.width(), img.depth()//8),
                     buffer = buffer,
                     dtype  = np.uint8)

    if share_memory:
        return arr
    else:
        return copy.deepcopy(arr)
