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

from PyQt5.QtWidgets import QTableView, QStyledItemDelegate
from PyQt5.QtGui import QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant

from config import config
from model.model import CodeArray


class Grid(QTableView):
    def __init__(self, main_window):
        super().__init__(main_window)

        self.main_window = main_window

        dimensions = (config["grid_rows"],
                      config["grid_columns"],
                      config["grid_tables"])

        window_position = config["window_position"]
        window_size = config["window_size"]

        self.setGeometry(*window_position, *window_size)

        self.code_array = CodeArray(dimensions)
        self.model = GridItemModel(main_window, self.code_array)
        self.setModel(self.model)

        self.model.dataChanged.connect(self.on_data_changed)
        self.selectionModel().currentChanged.connect(self.on_current_changed)

        self.verticalHeader().sectionResized.connect(self.on_row_resized)
        self.horizontalHeader().sectionResized.connect(self.on_column_resized)

        self.setShowGrid(False)

        delegate = GridCellDelegate(main_window, self.code_array)
        self.setItemDelegate(delegate)

    def set_current_index(self, row, column):
        """Sets the current index to row, column"""

        row_count = self.model.rowCount()
        column_count = self.model.rowCount()
        if 0 <= row < row_count and 0 <= column < column_count:
            index = self.model.index(row, column, QModelIndex())
            self.setCurrentIndex(index)

    def on_data_changed(self):
        """Event handler for data changes"""

        row = self.currentIndex().row()
        column = self.currentIndex().column()
        table = self.main_window.table
        code = self.code_array((row, column, table))
        self.main_window.entry_line.setText(code)

        if not self.main_window.application_states.changed_since_save:
            self.main_window.application_states.changed_since_save = True
            main_window_title = "* " + self.main_window.windowTitle()
            self.main_window.setWindowTitle(main_window_title)

    def on_current_changed(self, current, previous):
        """Event handler for change of current cell"""

        row = current.row()
        column = current.column()
        table = self.main_window.table
        code = self.code_array((row, column, table))
        self.main_window.entry_line.setText(code)

    def on_row_resized(self, row, old_height, new_height):
        """Row resized event handler"""

        table = self.main_window.table
        self.model.code_array.row_heights[(row, table)] = new_height

    def on_column_resized(self, column, old_width, new_width):
        """Row resized event handler"""

        table = self.main_window.table
        self.model.code_array.col_widths[(column, table)] = new_width


class GridItemModel(QAbstractTableModel):
    def __init__(self, main_window, code_array):
        super().__init__()

        self.main_window = main_window
        self.code_array = code_array

    def rowCount(self, parent=QModelIndex()):
        """Overloaded rowCount for code_array backend"""

        return self.code_array.shape[0]

    def columnCount(self, parent=QModelIndex()):
        """Overloaded columnCount for code_array backend"""

        return self.code_array.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        """Overloaded data for code_array backend"""

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            table = self.main_window.table

            value = self.code_array[row, column, table]

            if value is None:
                return ""
            else:
                return str(value)

        if role == Qt.BackgroundColorRole:
            row = index.row()
            column = index.column()
            table = self.main_window.table
            key = row, column, table
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
            table = self.main_window.table

            return self.code_array((row, column, table))

        return QVariant()

    def setData(self, index, value, role):
        """Overloaded setData for code_array backend"""

        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            table = self.main_window.table
            self.code_array[row, column, table] = "{}".format(value)
            self.dataChanged.emit(index, index)

            return True

    def flags(self, index):
        return QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable

    def headerData(self, idx, orientation, role):
        if role == Qt.DisplayRole:
            return str(idx)


class GridCellDelegate(QStyledItemDelegate):

    def __init__(self, main_window, code_array):
        super().__init__()

        self.main_window = main_window
        self.code_array = code_array
        self.cell_attributes = self.code_array.cell_attributes

    def _paint_text(self, rect, painter, option, index):
        """Paint text in cell"""

        row = index.row()
        column = index.column()
        table = self.main_window.table
        key = row, column, table

        res = self.code_array[key]
        if res is None:
            # Do not paint None values
            return

        textcolor_rgb = self.code_array.cell_attributes[key]["textcolor"]
        textcolor = QColor(*textcolor_rgb)
        painter.setPen(textcolor)

        textfont_name = self.code_array.cell_attributes[key]["textfont"]
        textfont_pointsize = self.code_array.cell_attributes[key]["pointsize"]
        textfont = QFont(textfont_name, textfont_pointsize)
        painter.setFont(textfont)

        painter.drawText(rect, Qt.AlignLeft, str(res))

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

        row = index.row()
        column = index.column()
        table = self.main_window.table

        # Paint bottom and right border lines of the current cell
        key = row, column, table
        self._paint_bl_border_lines(x, y, width, height, painter, key)

        # Paint bottom and right border lines of the cell above
        key = row - 1, column, table
        self._paint_bl_border_lines(x, y - height, width, height, painter, key)

        # Paint bottom and right border lines of the cell left
        key = row, column - 1, table
        self._paint_bl_border_lines(x - width, y, width, height, painter, key)

        # Paint bottom and right border lines of the current cell
        key = row - 1, column - 1, table
        self._paint_bl_border_lines(x - width, y - height, width, height,
                                    painter, key)

    def paint(self, painter, option, index):
#        QStyledItemDelegate.paint(self, painter, option, index)

        self._paint_text(option.rect, painter, option, index)
        self._paint_border_lines(option.rect, painter, index)


#    def createEditor(self, parent, option, index):
#        editor = QSpinBox(parent)
#        editor.setFrame(False)
#        editor.setMinimum(0)
#        editor.setMaximum(100)
#
#        return editor
#
    def setEditorData(self, editor, index):
        row = index.row()
        column = index.column()
        table = self.main_window.table

        value = self.code_array((row, column, table))
        editor.setText(value)
#
#    def setModelData(self, spinBox, model, index):
#        spinBox.interpretText()
#        value = spinBox.value()
#
#        model.setData(index, value, Qt.EditRole)
#
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
