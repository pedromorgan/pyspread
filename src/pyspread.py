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

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QSplitter
from PyQt5.QtGui import QColor, QFont

from icons import Icon
from grid import Grid
from entryline import Entryline
from menubar import MenuBar
from toolbar import MainToolBar, FindToolbar, AttributesToolbar, MacroToolbar
from toolbar import WidgetToolbar
from actions import MainWindowActions
from workflows import Workflows
from widgets import Widgets


class ApplicationStates:
    """Holds all global application states"""

    changed_since_save = False
    last_file_input_path = Path.home()
    last_file_output_path = Path.home()
    border_choice = "All borders"

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise AttributeError("{self} has no attribute {key}.".format(
                                 self=self, key=key))
        object.__setattr__(self, key, value)

    def reset(self):
        cls_attrs = (attr for attr in dir(self)
                     if not attr.startswith("__") and attr != "reset")
        for cls_attr in cls_attrs:
            setattr(self, cls_attr, getattr(ApplicationStates, cls_attr))


class MainWindow(QMainWindow):
    """Pyspread main window"""

    gui_update = pyqtSignal(dict)

    def __init__(self, application):
        super().__init__()

        self.application = application
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

        self.setGeometry(100, 100, 1000, 700)
        self.setWindowTitle('Pyspread')

    def _init_widgets(self):
        """Initialize widgets"""

        self.widgets = Widgets(self)

        self.entry_line = Entryline(self)
        self.grid = Grid(self)

        main_splitter = QSplitter(Qt.Vertical, self)
        self.setCentralWidget(main_splitter)

        main_splitter.addWidget(self.entry_line)
        main_splitter.addWidget(self.grid)
        main_splitter.addWidget(self.grid.table_choice)
        main_splitter.setSizes([self.entry_line.minimumHeight(), 9999, 20])

        self.gui_update.connect(self.on_gui_update)

    def _init_toolbars(self):
        """Initialize the main window toolbars"""

        self.main_toolbar = MainToolBar(self)
        self.find_toolbar = FindToolbar(self)
        self.attributes_toolbar = AttributesToolbar(self)
        self.macro_toolbar = MacroToolbar(self)
        self.widgets_toolbar = WidgetToolbar(self)

        self.addToolBar(self.main_toolbar)
        self.addToolBar(self.find_toolbar)
        self.addToolBarBreak()
        self.addToolBar(self.attributes_toolbar)
        self.addToolBar(self.macro_toolbar)
        self.addToolBar(self.widgets_toolbar)

    def closeEvent(self, event):
        """Overloaded close event, allows saving changes or canceling close"""

        self.workflows.file_quit()
        event.ignore()

    def on_nothing(self):
        """Dummy action that does nothing"""

        pass

    def on_gui_update(self, attributes):
        """GUI update event handler.

        Emmitted on cell change. Attributes contains current cell_attributes.

        """

        widgets = self.widgets

        is_bold = attributes["fontweight"] == QFont.Bold
        self.actions["bold"].setChecked(is_bold)

        is_italic = attributes["fontstyle"] == QFont.StyleItalic
        self.actions["italics"].setChecked(is_italic)

        underline_action = self.actions["underline"]
        underline_action.setChecked(attributes["underline"])

        strikethrough_action = self.actions["strikethrough"]
        strikethrough_action.setChecked(attributes["strikethrough"])

        renderer = attributes["renderer"]
        widgets.renderer_button.set_current_action(renderer)
        widgets.renderer_button.set_menu_checked(renderer)

        lock_action = self.actions["lock_cell"]
        lock_action.setChecked(attributes["locked"])
        self.entry_line.setReadOnly(attributes["locked"])

        rotation = "rotate_{angle}".format(angle=int(attributes["angle"]))
        widgets.rotate_button.set_current_action(rotation)
        widgets.rotate_button.set_menu_checked(rotation)
        widgets.justify_button.set_current_action(attributes["justification"])
        widgets.justify_button.set_menu_checked(attributes["justification"])
        widgets.align_button.set_current_action(attributes["vertical_align"])
        widgets.align_button.set_menu_checked(attributes["vertical_align"])

        border_action = self.actions.border_group.checkedAction()
        if border_action is not None:
            icon = border_action.icon()
            self.menuBar().border_submenu.setIcon(icon)
            self.attributes_toolbar.border_menu_button.setIcon(icon)

        border_width_action = self.actions.border_width_group.checkedAction()
        if border_width_action is not None:
            icon = border_width_action.icon()
            self.menuBar().line_width_submenu.setIcon(icon)
            self.attributes_toolbar.line_width_button.setIcon(icon)

        widgets.text_color_button.color = QColor(*attributes["textcolor"])
        widgets.background_color_button.color = QColor(*attributes["bgcolor"])
        widgets.font_combo.font = attributes["textfont"]
        widgets.font_size_combo.size = attributes["pointsize"]

        merge_cells_action = self.actions["merge_cells"]
        merge_cells_action.setChecked(attributes["merge_area"] is not None)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow(app)

    app.exec_()


if __name__ == '__main__':
    main()
