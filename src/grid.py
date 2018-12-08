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
from PyQt5.QtWidgets import QStyleOptionViewItem, QApplication, QStyle
from PyQt5.QtGui import QColor, QBrush, QPen, QFont
from PyQt5.QtGui import QAbstractTextDocumentLayout, QTextDocument
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtCore import QPointF, QRectF, QSize

from config import config
from model.model import CodeArray
from lib.selection import Selection
from lib.string_helpers import wrap_text


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

    def gui_update(self):
        """Emits gui update signal"""

        attributes = self.code_array.cell_attributes[self.current]
        self.main_window.gui_update.emit(attributes)

    def on_data_changed(self):
        """Event handler for data changes"""

        code = self.code_array(self.current)
        self.main_window.entry_line.setPlainText(code)

        if not self.main_window.application_states.changed_since_save:
            self.main_window.application_states.changed_since_save = True
            main_window_title = "* " + self.main_window.windowTitle()
            self.main_window.setWindowTitle(main_window_title)

    def on_current_changed(self, current, previous):
        """Event handler for change of current cell"""

        code = self.code_array(self.current)
        self.main_window.entry_line.setPlainText(code)
        self.gui_update()

    def on_row_resized(self, row, old_height, new_height):
        """Row resized event handler"""

        self.model.code_array.row_heights[(row, self.table)] = new_height
        self.gui_update()

    def on_column_resized(self, column, old_width, new_width):
        """Row resized event handler"""

        self.model.code_array.col_widths[(column, self.table)] = new_width
        self.gui_update()

    def on_font_changed(self):
        """Font change event handler"""

        font = self.main_window.widgets.font_combo.font

        attr = self.selection, self.table, {"textfont": font}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_font_size_changed(self):
        """Font size change event handler"""

        size = self.main_window.widgets.font_size_combo.size

        attr = self.selection, self.table, {"pointsize": size}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_bold_pressed(self, toggled):
        """Bold button pressed event handler"""

        fontweight = QFont.Bold if toggled else QFont.Normal

        attr = self.selection, self.table, {"fontweight": fontweight}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_italics_pressed(self, toggled):
        """Italics button pressed event handler"""

        fontstyle = QFont.StyleItalic if toggled else QFont.StyleNormal

        attr = self.selection, self.table, {"fontstyle": fontstyle}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_underline_pressed(self, toggled):
        """Underline button pressed event handler"""

        attr = self.selection, self.table, {"underline": toggled}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_strikethrough_pressed(self, toggled):
        """Strikethrough button pressed event handler"""

        attr = self.selection, self.table, {"strikethrough": toggled}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_markup_pressed(self, toggled):
        """Markup button pressed event handler"""

        attr = self.selection, self.table, {"markup": toggled}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_lock_pressed(self, toggled):
        """Lock button pressed event handler"""

        attr = self.selection, self.table, {"locked": toggled}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_rotate_0(self, toggled):
        """Rotate by 0° left button pressed event handler"""

        attr = self.selection, self.table, {"angle": 0.0}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_rotate_90(self, toggled):
        """Rotate by 0° left button pressed event handler"""

        attr = self.selection, self.table, {"angle": 90.0}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_rotate_180(self, toggled):
        """Rotate by 0° left button pressed event handler"""

        attr = self.selection, self.table, {"angle": 180.0}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_rotate_270(self, toggled):
        """Rotate by 0° left button pressed event handler"""

        attr = self.selection, self.table, {"angle": 270.0}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)

    def on_justify_left(self, toggled):
        """Justify left button pressed event handler"""

        attr = self.selection, self.table, {"justification": "justify_left"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_justify_fill(self, toggled):
        """Justify fill button pressed event handler"""

        attr = self.selection, self.table, {"justification": "justify_fill"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_justify_center(self, toggled):
        """Justify center button pressed event handler"""

        attr = self.selection, self.table, {"justification": "justify_center"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_justify_right(self, toggled):
        """Justify right button pressed event handler"""

        attr = self.selection, self.table, {"justification": "justify_right"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_align_top(self, toggled):
        """Align top button pressed event handler"""

        attr = self.selection, self.table, {"vertical_align": "align_top"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_align_middle(self, toggled):
        """Justify left button pressed event handler"""

        attr = self.selection, self.table, {"vertical_align": "align_center"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_align_bottom(self, toggled):
        """Justify left button pressed event handler"""

        attr = self.selection, self.table, {"vertical_align": "align_bottom"}
        self.model.setData(self.selected_idx, attr, Qt.TextAlignmentRole)
        self.gui_update()

    def on_text_color_changed(self):
        """Text color change event handler"""

        text_color = self.main_window.widgets.text_color_button.color
        text_color_rgb = text_color.getRgb()
        self.gui_update()

        attr = self.selection, self.table, {"textcolor": text_color_rgb}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)

    def on_line_color_changed(self):
        """Line color change event handler"""

        #TODO: selection =
        #TODO: Get selected borders to be set
        line_color = self.main_window.widgets.line_color_button.color
        line_color_rgb = line_color.getRgb()
        self.gui_update()

    def on_background_color_changed(self):
        """Background color change event handler"""

        bg_color = self.main_window.widgets.background_color_button.color
        bg_color_rgb = bg_color.getRgb()

        attr = self.selection, self.table, {"bgcolor": bg_color_rgb}
        self.model.setData(self.selected_idx, attr, Qt.DecorationRole)
        self.gui_update()

    def on_merge_pressed(self):
        """Merge cells button pressed event handler"""

        # This is not done in the model because setSpan does not work there

        bbox = self.selection.get_grid_bbox(self.code_array.shape)
        (top, left), (bottom, right) = bbox

        # Check if current cell is already merged
        if self.columnSpan(top, left) > 1 or self.rowSpan(top, left) > 1:
            self.setSpan(top, left, 1, 1)
            selection = Selection([], [], [], [], [(top, left)])
            attr = selection, self.table, {"merge_area": None}
        elif self.columnSpan(self.row, self.column) > 1 \
                or self.rowSpan(self.row, self.column) > 1:
            # Unmerge the cell that merges the current cell (!)
            self.setSpan(self.row, self.column, 1, 1)
            selection = Selection([], [], [], [], [(self.row, self.column)])
            attr = selection, self.table, {"merge_area": None}
        else:
            # Merge and store the current selection (!)
            self.setSpan(top, left, bottom-top+1, right-left+1)
            merging_selection = Selection([], [], [], [], [(top, left)])
            attr = merging_selection, self.table, {"merge_area":
                                                   (top, left, bottom, right)}
        self.code_array.cell_attributes.undoable_append(attr)


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
            value = self.code_array[key]
            return wrap_text(str(value) if value is not None else "")

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
                "justify_left": Qt.AlignLeft,
                "justify_center": Qt.AlignHCenter,
                "justify_right": Qt.AlignRight,
                "justify_fill": Qt.AlignJustify,
                "align_top": Qt.AlignTop,
                "align_center": Qt.AlignVCenter,
                "align_bottom": Qt.AlignBottom,
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

    def __paint(self, painter, option, index):
        """Calls the overloaded paint function or creates html delegate"""

        key = index.row(), index.column(), self.main_window.table
        if not self.cell_attributes[key]["markup"]:
            return super(GridCellDelegate, self).paint(painter, option, index)

        # HTML

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        if options.widget is None:
            style = QApplication.style()
        else:
            style = options.widget.style()

        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter,
                          options.widget)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        html_rect = style.subElementRect(QStyle.SE_ItemViewItemText, options,
                                         options.widget)
        painter.save()
        painter.translate(html_rect.topLeft())
        painter.setClipRect(html_rect.translated(-html_rect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """Overloads SizeHint"""

        key = index.row(), index.column(), self.main_window.table
        if not self.cell_attributes[key]["markup"]:
            return super(GridCellDelegate, self).sizeHint(option, index)

        # HTML
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QSize(doc.idealWidth(), doc.size().height())

    def _rotated_paint(self, painter, option, index, angle):
        """Paint cell contents for rotated cells"""

        # Rotate evryting by 90 degree

        optionCopy = QStyleOptionViewItem(option)
        rectCenter = QPointF(QRectF(option.rect).center())
        painter.save()
        painter.translate(rectCenter.x(), rectCenter.y())
        painter.rotate(angle)
        painter.translate(-rectCenter.x(), -rectCenter.y())
        optionCopy.rect = painter.worldTransform().mapRect(option.rect)

        # Call the base class paint method
        self.__paint(painter, optionCopy, index)

        painter.restore()

    def paint(self, painter, option, index):
        """Overloads QStyledItemDelegate to add cell border painting"""

        key = index.row(), index.column(), self.main_window.table
        angle = self.cell_attributes[key]["angle"]
        if abs(angle) < 0.001:
            # No rotation --> call the base class paint method
            self.__paint(painter, option, index)
        else:
            self._rotated_paint(painter, option, index, angle)

        self._paint_border_lines(option.rect, painter, index)

    def createEditor(self, parent, option, index):
        """Overloads QStyledItemDelegate to disable editor in frozen cells"""

        key = index.row(), index.column(), self.main_window.table
        if not self.cell_attributes[key]["locked"]:
            return super(GridCellDelegate, self).createEditor(parent, option,
                                                              index)

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
