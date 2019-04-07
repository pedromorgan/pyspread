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

"""

modal_dialogs
-------------

Modal dialogs for pyspread

"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog, QLineEdit
from PyQt5.QtWidgets import QLabel, QFormLayout, QVBoxLayout, QGroupBox
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtGui import QIntValidator, QImageWriter


class DiscardChangesDialog:
    """Modal dialog that asks if the user wants to discard or save unsaved data

    The modal dialog is shown on accessing the property choice.

    """

    title = "Unsaved changes"
    text = "There are unsaved changes.\nDo you want to save?"
    choices = QMessageBox.Discard | QMessageBox.Cancel | QMessageBox.Save
    default_choice = QMessageBox.Save

    def __init__(self, main_window):
        self.main_window = main_window

    @property
    def choice(self):
        """User choice

        Returns True iif the user confirms in a user dialog that unsaved
        changes will be discarded if conformed.
        Returns False iif the user chooses to save the unsaved data
        Returns None if the user chooses to abort the operation

        """

        button_approval = QMessageBox.warning(self.main_window, self.title,
                                              self.text, self.choices,
                                              self.default_choice)
        if button_approval == QMessageBox.Discard:
            return True
        elif button_approval == QMessageBox.Save:
            return False


class ApproveWarningDialog:
    """Modal warning dialog for approving files to be evaled

    The modal dialog is shown on accessing the property choice.

    """

    title = "Security warning"
    text = ("You are going to approve and trust a file that you have not "
            "created yourself. After proceeding, the file is executed.\n \n"
            "It may harm your system as any program can. Please check all "
            "cells thoroughly before proceeding.\n \n"
            "Proceed and sign this file as trusted?")
    choices = QMessageBox.No | QMessageBox.Yes
    default_choice = QMessageBox.No

    def __init__(self, parent):
        self.parent = parent

    @property
    def choice(self):
        """User choice

        Returns True iif the user approves leaving safe_mode.
        Returns False iif the user chooses to stay in safe_mode
        Returns None if the user chooses to abort the operation

        """

        button_approval = QMessageBox.warning(self.parent, self.title,
                                              self.text, self.choices,
                                              self.default_choice)
        if button_approval == QMessageBox.Yes:
            return True
        elif button_approval == QMessageBox.No:
            return False


class GridShapeDialog(QDialog):
    """Modal dialog for entering the number of rows, columns and tables

    Parameters
    ----------
    * parent: QWidget
    \tParent window
    * shape: 3-tuple of Integer
    \tInitial shape to be displayed in the dialog: (rows, columns, tables)

    """

    def __init__(self, parent, shape):
        super(GridShapeDialog, self).__init__(parent)

        self.shape = shape
        layout = QVBoxLayout(self)
        layout.addWidget(self.create_form())
        layout.addWidget(self.create_buttonbox())
        self.setLayout(layout)

        self.setWindowTitle("Create a new grid")

    def get_shape(self):
        """Executes the dialog and returns an int tuple rows, columns, tables

        Returns None if the dialog is canceled

        """

        result = self.exec_()

        if result == QDialog.Accepted:
            try:
                rows = int(self.row_edit.text())
                columns = int(self.column_edit.text())
                tables = int(self.table_edit.text())
            except ValueError:
                # At least one field was empty or contained no number
                return

            return rows, columns, tables

    def create_form(self):
        """Returns form inside a QGroupBox"""

        form_group_box = QGroupBox("Grid shape")
        form_layout = QFormLayout()

        validator = QIntValidator()
        validator.setBottom(0)  # Do not allow negative values

        self.row_edit = QLineEdit(str(self.shape[0]))
        self.row_edit.setAlignment(Qt.AlignRight)
        self.row_edit.setValidator(validator)
        form_layout.addRow(QLabel("Number of rows"), self.row_edit)

        self.column_edit = QLineEdit(str(self.shape[1]))
        self.column_edit.setAlignment(Qt.AlignRight)
        self.column_edit.setValidator(validator)
        form_layout.addRow(QLabel("Number of columns"), self.column_edit)

        self.table_edit = QLineEdit(str(self.shape[2]))
        self.table_edit.setAlignment(Qt.AlignRight)
        self.table_edit.setValidator(validator)
        form_layout.addRow(QLabel("Number of tables"), self.table_edit)

        form_group_box.setLayout(form_layout)

        return form_group_box

    def create_buttonbox(self):
        """Returns a QDialogButtonBox with Ok and Cancel"""

        button_box = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box


class FileDialogBase:
    """Base class for modal file dialogs

    The choosen filename is stored in the filepath attribute
    The choosen name filter is stored in the chosen_filter attribute
    If the dialog is aborted then both filepath and chosen_filter are None

    _get_filepath must be overloaded

    """

    title = "Choose file"
    name_filter = "Pyspread uncompressed (*.pysu);;" + \
                  "Pyspread compressed (*.pys)"
    filepath = None
    chosen_filter = None

    def __init__(self, main_window):
        self.main_window = main_window
        self.filepath, self.chosen_filter = self._get_filepath()


class FileOpenDialog(FileDialogBase):
    """Modal dialog for choosing a pyspread file"""

    title = "Open"

    def _get_filepath(self):
        """Returns (filepath, chosen_filter) from modal user dialog"""

        path = self.main_window.application_states.last_file_input_path
        filepath, chosen_filter = \
            QFileDialog.getOpenFileName(self.main_window, self.title,
                                        str(path), self.name_filter)
        return filepath, chosen_filter


class FileSaveDialog(FileDialogBase):
    """Modal dialog for choosing a pyspread save file"""

    title = "Save"

    def _get_filepath(self):
        """Returns (filepath, chosen_filter) from modal user dialog"""

        path = self.main_window.application_states.last_file_output_path
        filepath, chosen_filter = \
            QFileDialog.getSaveFileName(self.main_window, self.title,
                                        str(path), self.name_filter)
        return filepath, chosen_filter


class ImageFileOpenDialog(FileDialogBase):
    """Modal dialog for inserting an image"""

    title = "Insert image"

    img_formats = QImageWriter.supportedImageFormats()
    img_format_strings = ("*." + fmt.data().decode('utf-8')
                          for fmt in img_formats)
    img_format_string = " ".join(img_format_strings)
    name_filter = "Images ({})".format(img_format_string) + ";;" \
                  "Scalable Vector Graphics (*.svg *.svgz)"

    def _get_filepath(self):
        """Returns (filepath, chosen_filter) from modal user dialog"""

        path = self.main_window.application_states.last_file_input_path
        filepath, chosen_filter = \
            QFileDialog.getOpenFileName(self.main_window,
                                        self.title,
                                        str(path),
                                        self.name_filter)
        return filepath, chosen_filter
