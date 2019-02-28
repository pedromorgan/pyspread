#!/usr/bin/env python
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
pyspread config file
====================

"""

from PyQt5.QtCore import QSettings

VERSION = "2.0"


class DefaultSettings:
    """Contains default config for starting pyspread without resource file"""

    # Config file version
    # -------------------

    config_version = VERSION

    # Cell calculation timeout in s
    # -----------------------------
    timeout = 10

    # User defined paths
    # ------------------

    work_path = None

    # UI language
    # -----------

    ui_language = 'en'  # 'system' for system locale

    # Spell checking lamguage
    # -----------------------

    check_spelling = False
    spell_lang = 'en_US'

    # Default filetypes
    # -----------------

    default_open_filetype = 'pys'
    default_save_filetype = 'pys'

    # Window configuration
    # --------------------

    window_position = (10, 10)
    window_size = (800, 600)
    window_layout = ''
    icon_theme = 'Tango'

    help_window_position = (50, 50)
    help_window_size = (600, 400)

    # Grid configuration
    # ------------------

    grid_rows = 1000
    grid_columns = 100
    grid_tables = 3

    max_unredo = 5000

    timer_interval = 1000

    # Default row height and col width e.g. for Cairo rendering
    default_row_height = 23
    default_col_width = 80

    # Maximum result length in a cell in characters
    max_result_length = 100000

    # Colors
    grid_color = (192, 192, 192)
    background_color = (255, 255, 255)
    text_color = (0, 0, 0)
    freeze_color = (0, 0, 255)

    # Fonts

    font = "Sans"
    font_save_enabled = "False"

    # Default cell font size

    font_default_size = 10
    font_default_sizes = [6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32]

    # Zoom

    minimum_zoom = 0.25
    maximum_zoom = 8.0

    # Increase and decrease factor on zoom in and zoom out
    zoom_factor = 0.05

    # GPG parameters
    # --------------

    gpg_key_fingerprint = ''

    # CSV parameters for import and export
    # ------------------------------------

    # Number of bytes for the sniffer (should be larger than 1st+2nd line)
    sniff_size = 65536

    # Maximum number of characters in wx.TextCtrl
    max_textctrl_length = 65534


class Settings:
    """QT5 settings accessor"""

    settings = QSettings("pyspread", "pyspread")
    defaults = DefaultSettings()

    def __getattr__(self, name):
        try:
            value = self.settings.value(name)
            if value is not None:
                return value
        except AttributeError:
            pass  # Attribute not in stored settings

        return getattr(self.defaults, name)

    def __setattr__(self, name, value):
        self.settings.setValue(name, value)
        self.settings.sync()
