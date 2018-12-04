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
from builtins import object

from ast import literal_eval

VERSION = "2.0"


class DefaultConfig(object):
    """Contains default config for starting pyspread without resource file"""

    def __init__(self):
        # Config file version
        # -------------------

        self.config_version = VERSION

        # Cell calculation timeout in s
        # -----------------------------
        self.timeout = 10

        # User defined paths
        # ------------------

        standardpaths = None
        self.work_path = None

        # UI language
        # -----------

        self.ui_language = 'en'  # 'system' for system locale

        # Spell checking lamguage
        # -----------------------

        self.check_spelling = False
        self.spell_lang = 'en_US'

        # Default filetypes
        # -----------------

        self.default_open_filetype = 'pys'
        self.default_save_filetype = 'pys'

        # Window configuration
        # --------------------

        self.window_position = (10, 10)
        self.window_size = (800, 600)
        self.window_layout = ''
        self.icon_theme = 'Tango'

        self.help_window_position = (50, 50)
        self.help_window_size = (600, 400)

        # Grid configuration
        # ------------------

        self.grid_rows = 1000
        self.grid_columns = 100
        self.grid_tables = 3

        self.max_unredo = 5000

        self.timer_interval = 1000

        # Default row height and col width e.g. for Cairo rendering
        self.default_row_height = 23
        self.default_col_width = 80

        # Maximum result length in a cell in characters
        self.max_result_length = 100000

        # Colors
        self.grid_color = (192, 192, 192)
        self.background_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.freeze_color = (0, 0, 255)

        # Fonts

        self.font = "Sans"
        self.font_save_enabled = "False"

        # Default cell font size

        self.font_default_size = 10
        self.font_default_sizes = [6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32]

        # Zoom

        self.minimum_zoom = 0.25
        self.maximum_zoom = 8.0

        # Increase and decrease factor on zoom in and zoom out
        self.zoom_factor = 0.05

        # GPG parameters
        # --------------

        self.gpg_key_fingerprint = ''

        # CSV parameters for import and export
        # ------------------------------------

        # Number of bytes for the sniffer (should be larger than 1st+2nd line)
        self.sniff_size = 65536

        # Maximum number of characters in wx.TextCtrl
        self.max_textctrl_length = 65534


class Config(object):
    """Configuration class for the application pyspread"""

    # Only keys in default_config are config keys

    def __init__(self, defaults=None):
        self.config_filename = "pyspreadrc"

        # The current version of pyspread
        self.version = VERSION

        if defaults is None:
            self.defaults = DefaultConfig()

        else:
            self.defaults = defaults()

        self.data = DefaultConfig()

        self.cfg_file = None

        # Config keys to be resetted to default value on version upgrades
        self.reset_on_version_change = ["window_layout"]

        self.load()

    def __getitem__(self, key):
        """Main config element read access"""

        if key == "version":
            return self.version

        try:
            return getattr(self.data, key)

        except KeyError:
            # Probably, there is a problem with the config file --> use default
            setattr(self.data, key, getattr(DefaultConfig(), key))

            return getattr(self.data, key)

        except SyntaxError:
            # May happen if a file is not present any more

            return None

    def __setitem__(self, key, value):
        """Main config element write access"""

        setattr(self.data, key, value)

    def load(self):
        """Loads configuration file"""

#        # Reset data
#        self.data.__dict__.update(self.defaults.__dict__)
#
#        for key in self.defaults.__dict__:
#            if self.cfg_file.Exists(key):
#                setattr(self.data, key, self.cfg_file.Read(key))
#
#        # Reset keys that should be reset on version upgrades
#        for key in self.reset_on_version_change:
#            setattr(self.data, key, getattr(DefaultConfig(), key))
#        self.data.config_version = self.version
#
#        # Delete gpg_key_uid and insert fingerprint key
#
#        if hasattr(self.data, "gpg_key_uid"):
#            oldkey = "gpg_key_uid"
#            delattr(self.data, oldkey)
#            newkey = "gpg_key_fingerprint"
#            setattr(self.data, newkey, getattr(DefaultConfig(), newkey))

    def save(self):
        """Saves configuration file"""

#        for key in self.defaults.__dict__:
#            data = getattr(self.data, key)
#
#            self.cfg_file.Write(key, data)

config = Config()
