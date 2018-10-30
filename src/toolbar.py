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

from collections import OrderedDict

from PyQt5.QtWidgets import QToolBar


class MainToolBar(QToolBar):
    """The main toolbar for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self._create_toolbar(main_window.actions)

    def _create_toolbar(self, actions):
        """Fills the main toolbar with QActions"""

        self.addAction(actions["new"])
        self.addAction(actions["open"])
        self.addAction(actions["save"])
        self.addAction(actions["export"])
        self.addSeparator()
        self.addAction(actions["undo"])
        self.addAction(actions["redo"])
        self.addSeparator()
        self.addAction(actions["check_spelling"])
        self.addSeparator()
        self.addAction(actions["find"])
        self.addAction(actions["replace"])
        self.addSeparator()
        self.addAction(actions["cut"])
        self.addAction(actions["copy"])
        self.addAction(actions["copy_results"])
        self.addAction(actions["paste"])
        self.addAction(actions["paste"])
        self.addSeparator()
        self.addAction(actions["sort_ascending"])
        self.addAction(actions["sort_descending"])
        self.addSeparator()
        self.addAction(actions["print"])



class FindToolbar(QToolBar):
    """The find toolbar for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self._create_toolbar(main_window.actions)

    def _create_toolbar(self, actions):
        """Fills the find toolbar with QActions"""

        self.addSeparator()


class AttributesToolbar(QToolBar):
    """The attributes toolbar for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self._create_toolbar(main_window.actions)

    def _create_toolbar(self, actions):
        """Fills the attributes toolbar with QActions"""

        self.addAction(actions["bold"])
        self.addAction(actions["italics"])
        self.addAction(actions["underline"])
        self.addAction(actions["strikethrough"])
        self.addAction(actions["freeze_cell"])
        self.addAction(actions["lock_cell"])
        self.addAction(actions["merge_cells"])


class MacroToolbar(QToolBar):
    """The macro toolbar for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self._create_toolbar(main_window.actions)

    def _create_toolbar(self, actions):
        """Fills the macro toolbar with QActions"""

        self.addAction(actions["insert_image"])
        self.addAction(actions["link_image"])
        self.addAction(actions["insert_chart"])


class WidgetToolbar(QToolBar):
    """The widget toolbar for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self._create_toolbar(main_window.actions)

    def _create_toolbar(self, actions):
        """Fills the widget toolbar with QActions"""

        self.addSeparator()
