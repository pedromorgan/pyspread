#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 22:48:45 2018

@author: mn
"""

import random

from PyQt5.QtWidgets import QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtCore

from model.model import CodeArray

class Grid(QTableView):
    def __init__(self, parent):
        super().__init__(parent)

        dimensions = 1000, 100, 3

        self.setGeometry(0, 0, 575, 575)
        # SELECTING THE MODEL - FRAMEWORK THAT HANDLES QUERIES AND EDITS
        self.grid_item_model = GridItemModel(CodeArray(dimensions))
        self.setModel(self.grid_item_model)  # SETTING THE MODEL
        #grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.doubleClicked.connect(self.on_grid_click)
        #self.model.itemChanged.connect(self.on_state_changed)
#
#        self.populate()
#
#    def populate(self):
#        # GENERATE A 4x10 GRID OF RANDOM NUMBERS.
#        # VALUES WILL CONTAIN A LIST OF INT.
#        # MODEL ONLY ACCEPTS STRINGS - MUST CONVERT.
#        values = []
#        for i in range(10):
#            sub_values = []
#            for i in range(4):
#                value = random.randrange(1, 100)
#                sub_values.append(value)
#            values.append(sub_values)
#
#        for value in values:
#            row = []
#            for item in value:
#                cell = QStandardItem(str(item))
#                row.append(cell)
#            self.model.appendRow(row)

    def on_grid_click(self, signal):
        row = signal.row()  # RETRIEVES ROW OF CELL THAT WAS DOUBLE CLICKED
        column = signal.column()  # RETRIEVES COLUMN OF CELL THAT WAS DOUBLE CLICKED
        cell_dict = self.grid_item_model.itemData(signal)  # RETURNS DICT VALUE OF SIGNAL
        cell_value = cell_dict.get(0)  # RETRIEVE VALUE FROM DICT

        index = signal.sibling(row, 0)
        index_dict = self.grid_item_model.itemData(index)
        index_value = index_dict.get(0)

        print(
            'Row {}, Column {} clicked - value: {}\nColumn 1 contents: {}'.format(row, column, cell_value, index_value))

    def on_state_changed(self, signal):
        print(signal.row(), signal.column(), signal.text())


class GridItemModel(QtCore.QAbstractTableModel):
    def __init__(self, code_array):
        super().__init__()

        self.code_array = code_array

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.code_array.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.code_array.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        #print 'Data Call'
        #print index.column(), index.row()
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            #return QtCore.QVariant(str(self.datatable.iget_value(i, j)))
            value = self.code_array[row-1, column-1, 0]

            if value is None:
                return ""
            else:
                return str(value)
        else:
            return QtCore.QVariant()

    def setData(self, index, value, role):
#        if not index.isValid():
#            return False
#        elif role != QtCore.Qt.DisplayRole:
#            return False
        row = index.row()
        column = index.column()
        self.code_array[row-1, column-1, 0] = "{}".format(value)

        return True

    def flags(self, index):
        return QtCore.QAbstractTableModel.flags(self, index) | \
               QtCore.Qt.ItemIsEditable
