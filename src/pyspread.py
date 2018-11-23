#!/usr/bin/python3
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

========
pyspread
========

Python spreadsheet application

Run this script to start the application.

Provides
--------

* Commandlineparser: Gets command line options and parameters
* MainApplication: Initial command line operations and application launch

"""

from pathlib import Path
import sys

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QMainWindow, QApplication, QSplitter
from PyQt5.QtWidgets import QTabBar
from icons import Icon

from grid import Grid
from entryline import Entryline
from menubar import MenuBar
from toolbar import MainToolBar, FindToolbar, AttributesToolbar, MacroToolbar
from toolbar import WidgetToolbar
from actions import MainWindowActions
from workflows import Workflows


class ApplicationStates:
    """Holds all global application states"""

    changed_since_save = False
    last_file_input_directory = Path.home()
    last_file_output_directory = Path.home()

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise AttributeError("{self} has no attribute {key}.".format(
                                 self=self, key=key))
        object.__setattr__(self, key, value)


class MainWindow(QMainWindow):
    """Pyspread main window"""

    def __init__(self):
        super().__init__()

        self.application_states = ApplicationStates()
        self.workflows = Workflows(self)

        self._init_widgets()

        self.actions = MainWindowActions(self)

        self._init_window()
        self._init_toolbars()

        self.show()

    def _init_window(self):
        """Initialize main window components"""

        self.setWindowIcon(Icon("pyspread"))

        self.statusBar()
        self.setMenuBar(MenuBar(self))

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Pyspread')

    def _init_widgets(self):
        """Initialize widgets"""

        self.entry_line = Entryline(self)
        self.grid = Grid(self)
        self.table_choice = QTabBar(self, shape=QTabBar.RoundedSouth)
        self.table_choice.setExpanding(False)
        for i in range(self.grid.code_array.shape[2]):
            self.table_choice.addTab(str(i))

        main_splitter = QSplitter(Qt.Vertical, self)
        self.setCentralWidget(main_splitter)

        main_splitter.addWidget(self.entry_line)
        main_splitter.addWidget(self.grid)
        main_splitter.addWidget(self.table_choice)
        main_splitter.setSizes([self.entry_line.minimumHeight(), 9999, 20])

        self.table_choice.currentChanged.connect(self.on_table_changed)

    def _init_toolbars(self):
        """Initialize the main window toolbars"""

        self.addToolBar(MainToolBar(self))
        self.addToolBar(FindToolbar(self))
        self.addToolBarBreak()
        self.addToolBar(AttributesToolbar(self))
        self.addToolBar(MacroToolbar(self))
        self.addToolBar(WidgetToolbar(self))

    def on_nothing(self):
        """Dummy action that does nothing"""

        pass

    @property
    def table(self):
        """Returns current table from table_choice that is displayed"""

        return self.table_choice.currentIndex()

    def on_table_changed(self, current):
        """Event handler for table changes"""

        self.grid.model.dataChanged.emit(QModelIndex(), QModelIndex())


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    app.exec_()


if __name__ == '__main__':
    main()
