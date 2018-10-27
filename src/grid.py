#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 22:48:45 2018

@author: mn
"""

import random

from PyQt5.QtWidgets import QTableView, QStyledItemDelegate
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant

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
        self.setShowGrid(False)

        delegate = GridCellDelegate()
        self.setItemDelegate(delegate)


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


class GridItemModel(QAbstractTableModel):
    def __init__(self, code_array):
        super().__init__()

        self.code_array = code_array

    def rowCount(self, parent=QModelIndex()):
        return self.code_array.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self.code_array.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        #print 'Data Call'
        #print index.column(), index.row()
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            #return QVariant(str(self.datatable.iget_value(i, j)))
            value = self.code_array[row-1, column-1, 0]

            if value is None:
                return ""
            else:
                return str(value)

        if role==Qt.BackgroundColorRole:
            bgColor=QBrush(QColor(0, 0, 255), Qt.BDiagPattern)
            return bgColor

        if role==Qt.TextColorRole:
            return QColor(Qt.black)

        if role==Qt.ToolTipRole:
            return "Tooltip"

        if role==Qt.StatusTipRole:
            return "Statustip"

        return QVariant()

    def setData(self, index, value, role):
#        if not index.isValid():
#            return False
#        elif role != Qt.DisplayRole:
#            return False
        row = index.row()
        column = index.column()
        self.code_array[row-1, column-1, 0] = "{}".format(value)

        return True

    def flags(self, index):
        return QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable

    def headerData(self, idx, orientation, role):
        if role == Qt.DisplayRole:
            return str(idx)


class GridCellDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        QStyledItemDelegate.paint(self, painter, option, index)

        width = option.rect.width()
        height = option.rect.height()

        # Border lines
        top_line = (0, 0, width, 0)
        bottom_line = (0, height, width, height)
        left_line = (0, 0, 0, height)
        right_line = (width, 0, width, height)

        painter.save()
        painter.translate(option.rect.topLeft())
        painter.setPen(QPen(QBrush(Qt.red), 1))
        painter.drawLine(*top_line)
        painter.drawLine(*bottom_line)
        painter.drawLine(*left_line)
        painter.drawLine(*right_line)
        painter.restore()

#    def createEditor(self, parent, option, index):
#        editor = QSpinBox(parent)
#        editor.setFrame(False)
#        editor.setMinimum(0)
#        editor.setMaximum(100)
#
#        return editor
#
#    def setEditorData(self, spinBox, index):
#        value = index.model().data(index, Qt.EditRole)
#
#        spinBox.setValue(value)
#
#    def setModelData(self, spinBox, model, index):
#        spinBox.interpretText()
#        value = spinBox.value()
#
#        model.setData(index, value, Qt.EditRole)
#
#    def updateEditorGeometry(self, editor, option, index):
#        editor.setGeometry(option.rect)
