#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 14:43:54 2018

@author: mn
"""

from pathlib import PurePath
from PyQt5.QtGui import QIcon

PYSPREAD_PATH = PurePath('/home/mn/prog/pyspread')
ICON_PATH = PYSPREAD_PATH / 'share/icons'


class Icon(QIcon):
    """Class for getting items from names"""

    icon_path = {
        "pyspread": str(ICON_PATH / 'pyspread.ico'),

        "new": str(ICON_PATH / 'actions/filenew.svg'),
        "open": str(ICON_PATH / 'actions/fileopen.svg'),
        "save": str(ICON_PATH / 'actions/filesave.svg'),
        "save_as": str(ICON_PATH / 'actions/filesaveas.svg'),
        "approve": str(ICON_PATH / 'actions/approve.svg'),
        "clear_globals": str(ICON_PATH / 'actions/editclear.svg'),
        "print_preview": str(ICON_PATH / 'actions/fileprint.svg'),
        "print": str(ICON_PATH / 'actions/filequickprint.svg'),
        "preferences": str(ICON_PATH / 'actions/stock_properties.svg'),
        "new_gpg_key": str(ICON_PATH / 'actions/exit.svg'),
        "quit": str(ICON_PATH / 'actions/exit.svg'),
    }

    def __init__(self, name):
        super().__init__(self.icon_path[name])
