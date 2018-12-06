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
from lib.selection import Selection


class Grid(QTableView):
    """The main grid of pyspread"""

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

        # Signals
        self.model.dataChanged.connect(self.on_data_changed)
        self.selectionModel().currentChanged.connect(self.on_current_changed)

        self.main_window.widgets.text_color_button.colorChanged.connect(
                self.on_text_color_changed)
        self.main_window.widgets.background_color_button.colorChanged.connect(
                self.on_background_color_changed)
        self.main_window.widgets.line_color_button.colorChanged.connect(
                self.on_line_color_changed)
        self.main_window.widgets.font_combo.fontChanged.connect(
                self.on_font_changed)
        self.main_window.widgets.font_size_combo.fontSizeChanged.connect(
                self.on_font_size_changed)

        self.verticalHeader().sectionResized.connect(self.on_row_resized)
        self.horizontalHeader().sectionResized.connect(self.on_column_resized)

        self.setShowGrid(False)

        delegate = GridCellDelegate(main_window, self.code_array)
        self.setItemDelegate(delegate)

    @property
    def row(self):
        """Current row"""

        return self.currentIndex().row()

    @row.setter
    def row(self, value):
        """Sets current row to value"""

        self.current = value, self.column

    @property
    def column(self):
        """Current column"""

        return self.currentIndex().column()

    @column.setter
    def column(self, value):
        """Sets current column to value"""

        self.current = self.row, value

    @property
    def table(self):
        """Current table"""

        return self.main_window.table

    @table.setter
    def table(self, value):
        """Sets current table"""

        self.main_window.table = value

    @property
    def current(self):
        """Tuple of row, column, table of the current index"""

        return self.row, self.column, self.table

    @current.setter
    def current(self, value):
        """Sets the current index to row, column and if given table"""

        if len(value) == 2:
            row, column = value

        elif len(value) == 3:
            row, column, self.table = value

        else:
            msg = "Current cell must be defined with a tuple " + \
                  "(row, column) or (rol, column, table)."
            raise ValueError(msg)

        index = self.model.index(row, column, QModelIndex())
        self.setCurrentIndex(index)

    @property
    def selection(self):
        """Pyspread selection based on self's QSelectionModel"""

        selection = self.selectionModel().selection()

        block_top_left = []
        block_bottom_right = []
        cells = []

        # Selection are made of selection ranges that we call span

        for span in selection:
            top, bottom = span.top(), span.bottom()
            left, right = span.left(), span.right()

            # If the span is a single cell then append it
            if top == bottom and left == right:
                cells.append((top, right))
            else:
                # Otherwise append a block
                block_top_left.append((top, left))
                block_bottom_right.append((bottom, right))

        return Selection(block_top_left, block_bottom_right, [], [], cells)

    @property
    def selected_idx(self):
        """Currently selected indices"""
        return self.selectionModel().selectedIndexes()

    def on_data_changed(self):
        """Event handler for data changes"""

        code = self.code_array(self.current)
        self.main_window.entry_line.setText(code)

        if not self.main_window.application_states.changed_since_save:
            self.main_window.application_states.changed_since_save = True
            main_window_title = "* " + self.main_window.windowTitle()
            self.main_window.setWindowTitle(main_window_title)

    def on_current_changed(self, current, previous):
        """Event handler for change of current cell"""

        code = self.code_array(self.current)
        self.main_window.entry_line.setText(code)

        attributes = self.code_array.cell_attributes[self.current]
        self.main_window.gui_update.emit(attributes)

    def on_row_resized(self, row, old_height, new_height):
        """Row resized event handler"""

        self.model.code_array.row_heights[(row, self.table)] = new_height

    def on_column_resized(self, column, old_width, new_width):
        """Row resized event handler"""

        self.model.code_array.col_widths[(column, self.table)] = new_width

    def on_text_color_changed(self):
        """Text color change event handler"""

        text_color = self.main_window.widgets.text_color_button.color
        text_color_rgb = text_color.getRgb()

        attr = self.selection, self.table, {"textcolor": text_color_rgb}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_line_color_changed(self):
        """Line color change event handler"""

        #TODO: selection =
        #TODO: Get selected borders to be set
        line_color = self.main_window.widgets.line_color_button.color
        line_color_rgb = line_color.getRgb()

    def on_background_color_changed(self):
        """Background color change event handler"""

        bg_color = self.main_window.widgets.background_color_button.color
        bg_color_rgb = bg_color.getRgb()

        attr = self.selection, self.table, {"bgcolor": bg_color_rgb}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_font_changed(self):
        """Font change event handler"""

        font = self.main_window.widgets.font_combo.font

        attr = self.selection, self.table, {"textfont": font}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_font_size_changed(self):
        """Font size change event handler"""

        size = self.main_window.widgets.font_size_combo.size

        attr = self.selection, self.table, {"pointsize": size}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_bold_pressed(self, toggled):
        """Bold button pressed event handler"""

        fontweight = QFont.Bold if toggled else QFont.Normal

        attr = self.selection, self.table, {"fontweight": fontweight}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_italics_pressed(self, toggled):
        """Italics button pressed event handler"""

        fontstyle = QFont.StyleItalic if toggled else QFont.StyleNormal

        attr = self.selection, self.table, {"fontstyle": fontstyle}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_underline_pressed(self, toggled):
        """Underline button pressed event handler"""

        attr = self.selection, self.table, {"underline": toggled}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_strikethrough_pressed(self, toggled):
        """Strikethrough button pressed event handler"""

        attr = self.selection, self.table, {"strikethrough": toggled}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_justify_left(self, toggled):
        """Justify left button pressed event handler"""

        attr = self.selection, self.table, {"justification": "left"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)

    def on_justify_center(self, toggled):
        """Justify center button pressed event handler"""

        attr = self.selection, self.table, {"justification": "center"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)

    def on_justify_right(self, toggled):
        """Justify right button pressed event handler"""

        attr = self.selection, self.table, {"justification": "right"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)

    def on_align_top(self, toggled):
        """Align top button pressed event handler"""

        attr = self.selection, self.table, {"vertical_align": "top"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)

    def on_align_middle(self, toggled):
        """Justify left button pressed event handler"""

        attr = self.selection, self.table, {"vertical_align": "middle"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)

    def on_align_bottom(self, toggled):
        """Justify left button pressed event handler"""

        attr = self.selection, self.table, {"vertical_align": "bottom"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)


class GridItemModel(QAbstractTableModel):
    def __init__(self, main_window, code_array):
        super().__init__()

        self.main_window = main_window
        self.code_array = code_array

    def current(self, index):
        """Tuple of row, column, table of given index"""

        return index.row(), index.column(), self.main_window.table

    def rowCount(self, parent=QModelIndex()):
        """Overloaded rowCount for code_array backend"""

        return self.code_array.shape[0]

    def columnCount(self, parent=QModelIndex()):
        """Overloaded columnCount for code_array backend"""

        return self.code_array.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        """Overloaded data for code_array backend"""

        key = self.current(index)

        if role == Qt.DisplayRole:
            value = self.code_array[key]
            return str(value) if value is not None else ""

        if role == Qt.ToolTipRole:
            return self.code_array(self.current(index))

        if role == Qt.BackgroundColorRole:
            if self.code_array.cell_attributes[key]["frozen"]:
                pattern_rgb = config["freeze_color"]
                bg_color = QBrush(QColor(*pattern_rgb), Qt.BDiagPattern)
            else:
                bg_color_rgb = self.code_array.cell_attributes[key]["bgcolor"]
                bg_color = QColor(*bg_color_rgb)
            return bg_color

        if role == Qt.TextColorRole:
            text_color_rgb = self.code_array.cell_attributes[key]["textcolor"]
            return QColor(*text_color_rgb)

        if role == Qt.FontRole:
            attr = self.code_array.cell_attributes[key]
            text_font = attr["textfont"]
            pointsize = attr["pointsize"]
            fontweight = attr["fontweight"]
            italic = attr["fontstyle"]
            underline = attr["underline"]
            strikethrough = attr["strikethrough"]
            font = QFont(text_font, pointsize, fontweight, italic)
            font.setUnderline(underline)
            font.setStrikeOut(strikethrough)
            return font

        if role == Qt.TextAlignmentRole:
            pys2qt = {
                "left": Qt.AlignLeft,
                "center": Qt.AlignHCenter,
                "right": Qt.AlignRight,
                "justify": Qt.AlignJustify,
                "top": Qt.AlignTop,
                "middle": Qt.AlignVCenter,
                "bottom": Qt.AlignBottom,
            }
            attr = self.code_array.cell_attributes[key]
            alignment = pys2qt[attr["vertical_align"]]
            justification = pys2qt[attr["justification"]]
            alignment |= justification
            return alignment

        return QVariant()

    def setData(self, index, value, role):
        """Overloaded setData for code_array backend"""

        if role == Qt.EditRole:
            self.code_array[self.current(index)] = "{}".format(value)
            self.dataChanged.emit(index, index)

            return True

        if role == Qt.DecorationRole or role == Qt.TextAlignmentRole:
            self.code_array.cell_attributes.undoable_append(value)
            # We have a selection and no single cell
            for idx in index:
                self.dataChanged.emit(idx, idx)

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
        """Overloads QStyledItemDelegate to add cell border painting"""

        QStyledItemDelegate.paint(self, painter, option, index)
        self._paint_border_lines(option.rect, painter, index)

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

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
