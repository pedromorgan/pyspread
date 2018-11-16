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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QPlainTextEdit
from PyQt5.QtWidgets import QSplitter
from icons import Icon

from grid import Grid
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

        self.actions = MainWindowActions(self)
        self.application_states = ApplicationStates()
        self.workflows = Workflows(self)
        self.init_ui()

    def init_ui(self):

        self.setWindowIcon(Icon("pyspread"))

        self.entry_line = QPlainTextEdit(self)
        entry_line_min_height = \
            self.entry_line.cursorRect().y() + \
            self.entry_line.cursorRect().height() + 10
        self.entry_line.setMinimumHeight(entry_line_min_height)
        self.grid = Grid(self)

        main_splitter = QSplitter(Qt.Vertical, self)
        self.setCentralWidget(main_splitter)

        main_splitter.addWidget(self.entry_line)
        main_splitter.addWidget(self.grid)
        main_splitter.setSizes([entry_line_min_height, 9999])

        self.statusBar()
        self.setMenuBar(MenuBar(self))

        self.addToolBar(MainToolBar(self))
        self.addToolBar(FindToolbar(self))
        self.addToolBarBreak()
        self.addToolBar(AttributesToolbar(self))
        self.addToolBar(MacroToolbar(self))
        self.addToolBar(WidgetToolbar(self))

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Pyspread')

        self.grid.grid_item_model.dataChanged.connect(
                self.on_changed_since_save)

        self.show()

    def on_open(self):
        """File open event handler"""

        self.workflows.file_open()

    def on_nothing(self):
        """Dummy action that does nothing"""

        pass

    def on_changed_since_save(self):
        """Event handler that stores changed state"""

        if not self.application_states.changed_since_save:
            self.application_states.changed_since_save = True
            self.setWindowTitle("* " + self.windowTitle())


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    app.exec_()


if __name__ == '__main__':
    main()
