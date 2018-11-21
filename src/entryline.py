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


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit


class Entryline(QTextEdit):
    """The entry line for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        min_height = self.cursorRect().y() + self.cursorRect().height() + 20
        self.setMinimumHeight(min_height)

        self.setLineWrapMode(self.WidgetWidth)

    def keyPressEvent(self, event):
        """Key press event filter"""

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            index = self.main_window.grid.currentIndex()
            self.main_window.grid.model.setData(index, self.toPlainText(),
                                                Qt.EditRole)
            row, column = index.row(), index.column()
            self.main_window.grid.set_current_index(row+1, column)
        else:
            QTextEdit.keyPressEvent(self, event)
