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

from pathlib import Path

from PyQt5.QtWidgets import QMessageBox, QFileDialog


class DiscardChangesDialog:
    """Modal dialog that asks if the user wants to discard or save unsaved data

    The modal dialog is shown on __init__.
    Results can be retrieved in the discard attribute:
     * True iif the user confirms that unsaved changes shall be lost.
     * False iif the user chooses to save the unsaved data.
     * None iif the user chooses to abort the operation.

    """

    title = "Unsaved changes"
    text = "There are unsaved changes.\nDo you want to save?"
    choices = QMessageBox.Discard | QMessageBox.Cancel | QMessageBox.Save
    default_choice = QMessageBox.Save

    def __init__(self, main_window):
        self.main_window = main_window
        self.discard = self._get_discard_unsaved_changes_approval()

    def _get_discard_unsaved_changes_approval(self):
        """User alert dialog for proceeding though unsaved changes exist

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


class FileOpenDialog:
    """Modal dialog for choosing a pyspread save file

    The choosen filename is stored in the filepath attribute
    The choosen name filter is stored in the chosen_filter attribute
    If the dialog is aborted then both filepath and chosen_filter are None

    """

    title = "Open"
    name_filter = "Pyspread (*.pys *.pysu);;" + \
                  "Excel (*.xlsx *.xls);;" + \
                  "LibreOffice Calc (*.ods)"
    filepath = None
    chosen_filter = None

    def __init__(self, main_window):
        self.main_window = main_window
        self.filepath, self.chosen_filter = self._get_filepath()

    def _get_filepath(self):
        """Returns (filepath, chosen_filter) from modal user dialog"""

        path = self.main_window.application_states.last_file_input_directory
        filepath, chosen_filter = \
            QFileDialog.getOpenFileName(self.main_window, self.title,
                                        str(path), self.name_filter)
        return Path(filepath), chosen_filter
