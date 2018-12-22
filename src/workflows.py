#!/usr/bin/python3
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

workflows
---------

Workflows for pyspread

"""

import os.path

from modal_dialogs import DiscardChangesDialog, FileOpenDialog, GridShapeDialog


class Workflows:
    def __init__(self, main_window):
        self.main_window = main_window
        self.application_states = main_window.application_states

    def handle_changed_since_save(func):
        """Decorator to handle changes since last saving the document

        If changes are present then a dialog is displayed that asks if the
        changes shall be discarded.
        If the user selects Cancel then func is not executed.
        If the user selects Save then the file is saved and func is executed.
        If the user selects Discard then the file is not saved and func is
        executed.
        If no changes are present then func is directly executed.
        After executing func, reset_changed_since_save is called.

        """

        def function_wrapper(self):
            """Check changes and display and handle the dialog"""

            if self.application_states.changed_since_save:
                discard = DiscardChangesDialog(self.main_window).discard
                if discard is None:
                    return
                elif not discard:
                    self.file_save()
            func(self)
            self.reset_changed_since_save()

        return function_wrapper

    def reset_changed_since_save(self):
        """Sets changed_since_save to False and updates the window title"""

        # Change the main window filepath state
        self.application_states.changed_since_save = False

        # Get the current filepath
        filepath = self.application_states.last_file_input_path

        # Change the main window title
        window_title = "{filename} - pyspread".format(filename=filepath.name)
        self.main_window.setWindowTitle(window_title)

    @handle_changed_since_save
    def file_new(self):
        """File new workflow"""

        # Get grid shape from user
        old_shape = self.main_window.grid.code_array.shape
        shape = GridShapeDialog(self.main_window, old_shape).get_shape()
        if shape is None:
            # Abort changes because the dialog has been canceled
            return

        # Reset grid
        self.main_window.grid.model.reset()

        # Set new shape
        self.main_window.grid.model.shape = shape

        # Select upper left cell because initial selection behaves strange
        self.main_window.grid.reset_selection()

        # Reset application states
        self.application_states.reset()

    @handle_changed_since_save
    def file_open(self):
        """File open workflow"""

        # Get filepath from user
        file_open_dialog = FileOpenDialog(self.main_window)
        filepath = file_open_dialog.filepath
        chosen_filter = file_open_dialog.chosen_filter
        if filepath is None or not chosen_filter:
            return

        # Load file into grid
        print(filepath)
        print(os.path.getsize(filepath))
        with open(filepath, "rb") as infile:
            infile.seek(0, 2)  # EOF
            print(infile.tell())

        # Change the main window last input directory state
        self.application_states.last_file_input_path = filepath

    def file_save(self):
        """File save workflow"""

        raise NotImplementedError
