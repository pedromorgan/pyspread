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

from config import config
from model.model import CodeArray


class Grid(QTableView):
    def __init__(self, parent):
        super().__init__(parent)

        dimensions = (config["grid_rows"],
                      config["grid_columns"],
                      config["grid_tables"])

        window_position = config["window_position"]
        window_size = config["window_size"]

        self.setGeometry(*window_position, *window_size)
        # SELECTING THE MODEL - FRAMEWORK THAT HANDLES QUERIES AND EDITS
        self.code_array = CodeArray(dimensions)
        self.grid_item_model = GridItemModel(self.code_array)
        self.setModel(self.grid_item_model)  # SETTING THE MODEL
        # grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.doubleClicked.connect(self.on_grid_click)
        # self.model.itemChanged.connect(self.on_state_changed)
        self.setShowGrid(False)

        delegate = GridCellDelegate(self.code_array)
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
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()

            value = self.code_array[row-1, column-1, 0]

            if value is None:
                return ""
            else:
                return str(value)

        if role == Qt.BackgroundColorRole:
            row = index.row()
            column = index.column()
            key = row, column, 0
            if False:
                pattern_rgb = config["freeze_color"]
                bg_color = QBrush(QColor(*pattern_rgb), Qt.BDiagPattern)
            else:
                bg_color_rgb = self.code_array.cell_attributes[key]["bgcolor"]
                bg_color = QColor(*bg_color_rgb)
            return bg_color

        if role == Qt.TextColorRole:
            return QColor(Qt.black)

        if role == Qt.ToolTipRole:
            return "Tooltip"

        if role == Qt.StatusTipRole:
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

    def __init__(self, code_array):
        super().__init__()

        self.code_array = code_array

    def _paint_border_lines(self, rect, painter, index):
        """Paint bottom and right border lines around the cell"""

        key = index.row, index.column, 0

        cell_attributes = self.code_array.cell_attributes

        width = rect.width() - 1
        height = rect.height() - 1

        border_bottom = (0, height, width, height)
        border_right = (width, 0, width, height)

        bordercolor_bottom = cell_attributes[key]["bordercolor_bottom"]
        bordercolor_right = cell_attributes[key]["bordercolor_right"]

        borderwidth_bottom = cell_attributes[key]["borderwidth_bottom"]
        borderwidth_right = cell_attributes[key]["borderwidth_right"]

        painter.save()
        painter.translate(rect.topLeft())

        painter.setPen(QPen(QBrush(QColor(*bordercolor_bottom)),
                            borderwidth_bottom))
        painter.drawLine(*border_bottom)

        painter.setPen(QPen(QBrush(QColor(*bordercolor_right)),
                            borderwidth_right))
        painter.drawLine(*border_right)

        painter.restore()

    def paint(self, painter, option, index):
        QStyledItemDelegate.paint(self, painter, option, index)

        self._paint_border_lines(option.rect, painter, index)

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
