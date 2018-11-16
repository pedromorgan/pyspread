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

import lib.filetypes as filetypes


class Workflows:
    def __init__(self, main_window):
        self.main_window = main_window
        self.application_states = main_window.application_states

    def file_open(self):
        """File open workflow"""

        # If changes have taken place save of old grid
        if self.application_states.changed_since_save and \
           not self._get_unsaved_changes_approval():
            return

        # Get filepath from user

        # Change the main window filepath state

        # Load file into grid

        # Mark content as unchanged

    def _get_unsaved_changes_approval(self):
        """User alert dialog for proceeding though unsaved changes exist

        Returns True iif the user confirms in a user dialog that unsaved
        changes will be lost if conformed.

        """

        raise NotImplementedError

    def _get_file_path(self, title, filetype):
        """User dialog that asks if unsaved changes shall be lost

        Parameters
        ----------
        * filetype: String from available filetypes
        \tSpecifies the filetype.

        Wildcards
        ---------
         * pys:
         * pysu
         * csv
         * svg
         * xls

        """

        ft2wildcards = filetypes.get_filetypes2wildcards([filetype])

        wildcards = ft2wildcards[filetype]

        raise NotImplementedError