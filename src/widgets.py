#!/usr/bin/env python3
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


from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtWidgets import QPushButton, QColorDialog
from PyQt5.QtGui import QPalette, QColor

from icons import Icon

from config import config


class ColorButton(QPushButton):
    """Color button widget

    Parameters
    ----------

    * qcolor: QColor
    \tColor that is initially set
    * icon: QIcon, defaults to None
    \tButton foreground image
    * max_size: QSize, defaults to QSize(28, 28)
    \tMaximum Size of the button

    """

    colorChanged = pyqtSignal()
    title = "Select color"

    def __init__(self, color, icon=None, max_size=QSize(28, 28)):
        super().__init__()

        if icon is not None:
            self.setIcon(icon)

        self.color = color

        self.pressed.connect(self.on_pressed)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        """Color setter that adjusts internal state and button background.

        Parameters
        ----------
        * color: QColor
        \tNew color attribute to be set
        """

        if hasattr(self, "_color") and self._color == color:
            return

        self._color = color

        palette = self.palette()
        palette.setColor(QPalette.Button, color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.update()

    def set_max_size(self, size):
        """Set the maximum size of the widget

        size: Qsize
        \tMaximum size of the widget

        """

        self.setMaximumWidth(size.width())
        self.setMaximumHeight(size.height())

    def on_pressed(self):
        """Button pressed event handler

        Shows color dialog and sets the chosen color.

        """

        dlg = QColorDialog(self)
        dlg.setCurrentColor(self.color)
        dlg.setWindowTitle(self.title)

        if dlg.exec_():
            self.color = dlg.currentColor()
            self.colorChanged.emit()


class TextColorButton(ColorButton):
    """Color button with text icon"""

    def __init__(self, color):
        icon = Icon("text_color")
        super().__init__(color, icon=icon)

        self.title = "Select text color"
        self.setStatusTip("Text color")


class LineColorButton(ColorButton):
    """Color button with text icon"""

    def __init__(self, color):
        icon = Icon("line_color")
        super().__init__(color, icon=icon)

        self.title = "Select cell border line color"
        self.setStatusTip("Cell border line color")


class BackgroundColorButton(ColorButton):
    """Color button with text icon"""

    def __init__(self, color):
        icon = Icon("background_color")
        super().__init__(color, icon=icon)

        self.title = "Select cell background color"
        self.setStatusTip("Cell background color")


class Widgets:
    def __init__(self, main_window):
        text_color = QColor(*config["text_color"])
        self.text_color_button = TextColorButton(text_color)

        background_color = QColor(*config["background_color"])
        self.background_color_button = BackgroundColorButton(background_color)

        line_color = QColor(*config["grid_color"])
        self.line_color_button = LineColorButton(line_color)

        main_window.gui_update.connect(self.on_gui_update)

    def on_gui_update(self, attributes):
        """GUI update event handler.

        Emmitted on cell change. Attributes contains current cell_attributes.

        """

        self.text_color_button.color = QColor(*attributes["textcolor"])
        self.background_color_button.color = QColor(*attributes["bgcolor"])
