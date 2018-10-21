#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Pyspread QT transition tryout

"""

import sys
import random

from PyQt5.QtWidgets import QMainWindow, QTableView, QApplication
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from icons import Icon

from menubar import MenuBar
from toolbar import ToolBar
from actions import MainWindowActions


class MainWindow(QMainWindow):
    """Pyspread main window"""

    def __init__(self):
        super().__init__()

        self.actions = MainWindowActions(self)
        self.init_ui()

    def init_ui(self):

        self.setWindowIcon(Icon("pyspread"))

        grid = QTableView(self)
        grid.setGeometry(0, 0, 575, 575)
        # SELECTING THE MODEL - FRAMEWORK THAT HANDLES QUERIES AND EDITS
        self.model = QStandardItemModel(self)
        grid.setModel(self.model)  # SETTING THE MODEL
        grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        grid.doubleClicked.connect(self.on_grid_click)

        self.setCentralWidget(grid)

        self.populate_grid()

        self.statusBar()
        self.setMenuBar(MenuBar(self))
        self.addToolBar(ToolBar(self))

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Pyspread')
        self.show()

    def populate_grid(self):
        # GENERATE A 4x10 GRID OF RANDOM NUMBERS.
        # VALUES WILL CONTAIN A LIST OF INT.
        # MODEL ONLY ACCEPTS STRINGS - MUST CONVERT.
        values = []
        for i in range(10):
            sub_values = []
            for i in range(4):
                value = random.randrange(1, 100)
                sub_values.append(value)
            values.append(sub_values)

        for value in values:
            row = []
            for item in value:
                cell = QStandardItem(str(item))
                row.append(cell)
            self.model.appendRow(row)

    def on_grid_click(self, signal):
        row = signal.row()  # RETRIEVES ROW OF CELL THAT WAS DOUBLE CLICKED
        column = signal.column()  # RETRIEVES COLUMN OF CELL THAT WAS DOUBLE CLICKED
        cell_dict = self.model.itemData(signal)  # RETURNS DICT VALUE OF SIGNAL
        cell_value = cell_dict.get(0)  # RETRIEVE VALUE FROM DICT

        index = signal.sibling(row, 0)
        index_dict = self.model.itemData(index)
        index_value = index_dict.get(0)
        print(
            'Row {}, Column {} clicked - value: {}\nColumn 1 contents: {}'.format(row, column, cell_value, index_value))

    def nothing(self):
        pass


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
