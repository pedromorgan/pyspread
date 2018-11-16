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

from modal_dialogs import DiscardChangesDialog, FileOpenDialog


class Workflows:
    def __init__(self, main_window):
        self.main_window = main_window
        self.application_states = main_window.application_states

    def file_open(self):
        """File open workflow"""

        # If changes have taken place save of old grid
        if self.application_states.changed_since_save:
            discard = DiscardChangesDialog(self.main_window).discard
            if discard is None:
                return
            elif not discard:
                self.file_save()

        # Get filepath from user
        file_open_dialog = FileOpenDialog(self.main_window)
        filepath = file_open_dialog.filepath
        chosen_filter = file_open_dialog.chosen_filter
        if filepath is None or chosen_filter is None:
            return

        # Load file into grid


        # Change the main window filepath state
        self.application_states.changed_since_save = False

        # Change the main window last input directory state
        self.application_states.last_file_input_directory = filepath

        # Change the main window title
        window_title = "{filename} - pyspread".format(filename=filepath.name)
        self.main_window.setWindowTitle(window_title)

    def file_save(self):
        """File save workflow"""

        raise NotImplementedError
