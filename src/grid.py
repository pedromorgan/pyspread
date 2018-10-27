#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 22:48:45 2018

@author: mn
"""

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

        self.code_array = CodeArray(dimensions)
        self.grid_item_model = GridItemModel(self.code_array)
        self.setModel(self.grid_item_model)  # SETTING THE MODEL

        self.doubleClicked.connect(self.on_grid_click)
        # self.model.itemChanged.connect(self.on_state_changed)

        self.setShowGrid(False)

        delegate = GridCellDelegate(self.code_array)
        self.setItemDelegate(delegate)

    def on_grid_click(self, signal):
        row = signal.row()
        column = signal.column()
        cell_dict = self.grid_item_model.itemData(signal)
        cell_value = cell_dict.get(0)

        index = signal.sibling(row, 0)
        index_dict = self.grid_item_model.itemData(index)
        index_value = index_dict.get(0)

        print('Row {}, Column {} clicked - value: {}\nColumn 1 contents: {}'.
              format(row, column, cell_value, index_value))

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

            value = self.code_array[row, column, 0]

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
            row = index.row()
            column = index.column()

            return self.code_array((row, column, 0))

        return QVariant()

    def setData(self, index, value, role):
        row = index.row()
        column = index.column()
        self.code_array[row, column, 0] = "{}".format(value)

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
        self.cell_attributes = self.code_array.cell_attributes

    def _paint_bl_border_lines(self, x, y, width, height, painter, key):
        """Paint the bottom and the left border line of the cell"""

        border_bottom = (x, y + height, x + width, y + height)
        border_right = (x + width, y, x + width, y + height)

        bordercolor_bottom = self.cell_attributes[key]["bordercolor_bottom"]
        bordercolor_right = self.cell_attributes[key]["bordercolor_right"]

        borderwidth_bottom = self.cell_attributes[key]["borderwidth_bottom"]
        borderwidth_right = self.cell_attributes[key]["borderwidth_right"]

        painter.setPen(QPen(QBrush(QColor(*bordercolor_bottom)),
                            borderwidth_bottom))
        painter.drawLine(*border_bottom)

        painter.setPen(QPen(QBrush(QColor(*bordercolor_right)),
                            borderwidth_right))
        painter.drawLine(*border_right)

    def _paint_border_lines(self, rect, painter, index):
        """Paint border lines around the cell

        First, bottom and right border lines are painted.
        Next, border lines of the cell above are painted.
        Next, border lines of the cell left are painted.
        Finally, bottom and right border lines of the cell above left
        are painted.

        """

        x = rect.x() - 1
        y = rect.y() - 1
        width = rect.width()
        height = rect.height()

        # Paint bottom and right border lines of the current cell
        key = index.row(), index.column(), 0
        self._paint_bl_border_lines(x, y, width, height, painter, key)

        # Paint bottom and right border lines of the cell above
        key = index.row() - 1, index.column(), 0
        self._paint_bl_border_lines(x, y - height, width, height, painter, key)

        # Paint bottom and right border lines of the cell left
        key = index.row(), index.column() - 1, 0
        self._paint_bl_border_lines(x - width, y, width, height, painter, key)

        # Paint bottom and right border lines of the current cell
        key = index.row() - 1, index.column() - 1, 0
        self._paint_bl_border_lines(x - width, y - height, width, height,
                                    painter, key)

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
