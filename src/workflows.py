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

import bz2
from contextlib import contextmanager
import os.path
from shutil import move
import sys
from tempfile import NamedTemporaryFile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog, QMessageBox

from modal_dialogs import DiscardChangesDialog, FileOpenDialog, GridShapeDialog
from modal_dialogs import FileSaveDialog
from interfaces.pys import PysReader, PysWriter
from lib.gpg import verify


class Workflows:
    def __init__(self, main_window):
        self.main_window = main_window
        self.application_states = main_window.application_states

    @contextmanager
    def progress_dialog(self, title, label, maximum, min_duration=3000):
        """Context manager that displays a file progress dialog"""

        progress_dialog = QProgressDialog(self.main_window)
        progress_dialog.setWindowTitle(title)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setLabelText(label)
        progress_dialog.setMaximum(maximum)
        progress_dialog.setMinimumDuration(min_duration)
        progress_dialog.show()
        progress_dialog.setValue(0)

        yield progress_dialog

        progress_dialog.setValue(maximum)

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

        # Exit safe mode
        self.main_window.safe_mode = False

    @handle_changed_since_save
    def file_open(self):
        """File open workflow"""

        code_array = self.main_window.grid.code_array

        # Get filepath from user
        file_open_dialog = FileOpenDialog(self.main_window)
        filepath = file_open_dialog.filepath
        chosen_filter = file_open_dialog.chosen_filter
        if filepath is None or not chosen_filter:
            return
        filesize = os.path.getsize(filepath)

        # Reset grid
        self.main_window.grid.model.reset()

        # Is the file signed properly?
        self.main_window.safe_mode = not verify(filepath)

        # File compression handling
        if chosen_filter == "Pyspread uncompressed (*.pysu)":
            fopen = open
        else:
            fopen = bz2.open

        # Process events before showing the modal progress dialog
        self.main_window.application.processEvents()

        # Load file into grid
        with fopen(filepath, "rb") as infile:
            with self.progress_dialog("File open progress",
                                      "Opening {}...".format(filepath.name),
                                      filesize) as progress_dialog:
                for line in PysReader(infile, code_array):
                    progress_dialog.setValue(infile.tell())
                    self.main_window.application.processEvents()
                    if progress_dialog.wasCanceled():
                        self.main_window.grid.model.reset()
                        self.main_window.safe_mode = False
                        break

        # Explicitly set the grid shape
        shape = self.main_window.grid.code_array.shape
        self.main_window.grid.model.shape = shape

        # Update the cell spans because this is unsupported by the model
        self.main_window.grid.update_cell_spans()

        # Select upper left cell because initial selection behaves strangely
        self.main_window.grid.reset_selection()

        # Reset application states
        self.application_states.reset()

        # Change the main window last input directory state
        self.application_states.last_file_input_path = filepath

    def file_save(self):
        """File save workflow"""

        code_array = self.main_window.grid.code_array

        # Get filepath from user
        file_save_dialog = FileSaveDialog(self.main_window)
        filepath = file_save_dialog.filepath
        chosen_filter = file_save_dialog.chosen_filter

        # Extend filepath suffix if needed
        if chosen_filter == "Pyspread uncompressed (*.pysu)":
            if not filepath.suffix == '.pysu':
                filepath = filepath.with_suffix(filepath.suffix + '.pysu')
        else:
            # File compression handling
            compressor = bz2.BZ2Compressor()
            if not filepath.suffix == '.pys':
                filepath = filepath.with_suffix(filepath.suffix + '.pys')

        # Process events before showing the modal progress dialog
        self.main_window.application.processEvents()

        # Save grid to temporary file
        with NamedTemporaryFile(delete=False) as tempfile:
            filename = tempfile.name
            try:
                pys_writer = PysWriter(code_array)
                with self.progress_dialog("File save progress",
                                          "Saving {}...".format(filepath.name),
                                          len(pys_writer)) as progress_dialog:
                    for i, line in enumerate(pys_writer):
                        if chosen_filter != "Pyspread uncompressed (*.pysu)":
                            line = compressor.compress(line)
                            compressor.flush()
                        tempfile.write(line.encode('utf-8'))
                        progress_dialog.setValue(i)
                        self.main_window.application.processEvents()
                        if progress_dialog.wasCanceled():
                            tempfile.delete = True  # Delete incomplete tmpfile
                            return
            except (IOError, ValueError) as err:
                tempfile.delete = True
                QMessageBox.critical(self.main_window, "Error saving file",
                                     err)
                return
        try:
            move(filename, filepath)

        except OSError as err:
            # No tmp file present
            QMessageBox.critical(self.main_window, "Error saving file", err)

    @handle_changed_since_save
    def file_quit(self):
        """Program exit workflow"""

        sys.exit()
