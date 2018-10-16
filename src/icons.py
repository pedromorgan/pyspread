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
ACTION_PATH = ICON_PATH / 'actions'


class Icon(QIcon):
    """Class for getting items from names"""

    icon_path = {
        "pyspread": str(ICON_PATH / 'pyspread.svg'),

        # File menu icons
        "new": str(ACTION_PATH / 'document-new.svg'),
        "open": str(ACTION_PATH / 'document-open.svg'),
        "save": str(ACTION_PATH / 'document-save.svg'),
        "save_as": str(ACTION_PATH / 'document-save-as.svg'),
        "import": str(ACTION_PATH / 'document-import.svg'),
        "export": str(ACTION_PATH / 'document-export.svg'),
        "approve": str(ACTION_PATH / 'approve.svg'),
        "clear_globals": str(ACTION_PATH / 'edit-clear.svg'),
        "page_setup": str(ACTION_PATH / 'page-setup.svg'),
        "print_preview": str(ACTION_PATH / 'document-print-preview.svg'),
        "print": str(ACTION_PATH / 'document-print.svg'),
        "preferences": str(ACTION_PATH / 'document-properties.svg'),
        "new_gpg_key": str(ACTION_PATH / 'new-gpg-key.svg'),
        "quit": str(ACTION_PATH / 'system-log-out.svg'),

        # Edit menu icons
        "undo": str(ACTION_PATH / 'edit-undo.svg'),
        "redo": str(ACTION_PATH / 'edit-redo.svg'),
        "cut": str(ACTION_PATH / 'edit-cut.svg'),
        "copy": str(ACTION_PATH / 'edit-copy.svg'),
        "copy_results": str(ACTION_PATH / 'edit-copy-results.svg'),
        "paste": str(ACTION_PATH / 'edit-paste.svg'),
        "paste_as": str(ACTION_PATH / 'edit-paste-as.svg'),
        "select_all": str(ACTION_PATH / 'edit-select-all.svg'),
        "find": str(ACTION_PATH / 'edit-find.svg'),
        "replace": str(ACTION_PATH / 'edit-find-replace.svg'),
        "quote": str(ACTION_PATH / 'quote.svg'),
        "sort_ascending": str(ACTION_PATH / 'sort-ascending.svg'),
        "sort_descending": str(ACTION_PATH / 'sort-descending.svg'),
        "insert_row": str(ACTION_PATH / 'insert-row.svg'),
        "insert_column": str(ACTION_PATH / 'insert-column.svg'),
        "insert_table": str(ACTION_PATH / 'insert-table.svg'),
        "delete_row": str(ACTION_PATH / 'delete-row.svg'),
        "delete_column": str(ACTION_PATH / 'delete-column.svg'),
        "delete_table": str(ACTION_PATH / 'delete-table.svg'),
        "resize_grid": str(ACTION_PATH / 'resize-grid.svg'),

        # View menu icons
        "fullscreen": str(ACTION_PATH / 'view-fullscreen.svg'),
        "goto_cell": str(ACTION_PATH / 'goto-cell.svg'),
        "check_spelling": str(ACTION_PATH / 'check-spelling.svg'),
        "zoom_in": str(ACTION_PATH / 'zoom-in.svg'),
        "zoom_out": str(ACTION_PATH / 'zoom-out.svg'),
        "zoom_1": str(ACTION_PATH / 'zoom-original.svg'),
        "zoom_fit": str(ACTION_PATH / 'zoom-fit-best.svg'),
        "refresh": str(ACTION_PATH / 'view-refresh.svg'),
        "toggle_periodic_updates": str(ACTION_PATH / 'timer.svg'),
        "show_frozen": str(ACTION_PATH / 'show-frozen.svg'),

        # Format menu icons
        "copy_format": str(ACTION_PATH / 'edit-copy-format.svg'),
        "paste_format": str(ACTION_PATH / 'edit-paste-format.svg'),
        "font_dialog": str(ACTION_PATH / 'preferences-desktop-font.svg'),
        "bold": str(ACTION_PATH / 'format-text-bold.svg'),
        "italics": str(ACTION_PATH / 'format-text-italic.svg'),
        "underline": str(ACTION_PATH / 'format-text-underline.svg'),
        "strikethrough": str(ACTION_PATH / 'format-text-strikethrough.svg'),
        "markup": str(ACTION_PATH / 'format-text-markup.svg'),
        "text_color": str(ACTION_PATH / 'format-text-color.svg'),
        "background_color": str(ACTION_PATH / 'format-background-color.svg'),
        "justify_left": str(ACTION_PATH / 'format-justify-left.svg'),
        "justify_center": str(ACTION_PATH / 'format-justify-center.svg'),
        "justify_right": str(ACTION_PATH / 'format-justify-right.svg'),
        "align_top": str(ACTION_PATH / 'format-text-align-top.svg'),
        "align_center": str(ACTION_PATH / 'format-text-align-center.svg'),
        "align_bottom": str(ACTION_PATH / 'format-text-align-bottom.svg'),
        "rotate_0": str(ACTION_PATH / 'format-text-rotate-0.svg'),
        "rotate_90": str(ACTION_PATH / 'format-text-rotate-90.svg'),
        "rotate_180": str(ACTION_PATH / 'format-text-rotate-180.svg'),
        "rotate_270": str(ACTION_PATH / 'format-text-rotate-270.svg'),
        "freeze": str(ACTION_PATH / 'snowflake.svg'),
        "lock": str(ACTION_PATH / 'lock.svg'),
        "merge_cells": str(ACTION_PATH / 'merge-cells.svg'),

        # Macro menu icons
        "load_macros": str(ACTION_PATH / 'macro-open.svg'),
        "save_macros": str(ACTION_PATH / 'macro-save.svg'),
        "insert_image": str(ACTION_PATH / 'insert-image.svg'),
        "link_image": str(ACTION_PATH / 'link-image.svg'),
        "insert_chart": str(ACTION_PATH / 'insert-chart.svg'),

        # Help menu icons
        "help": str(ACTION_PATH / 'help-browser.svg'),
        "tutorial": str(ACTION_PATH / 'help-tutorial.svg'),
        "faq": str(ACTION_PATH / 'help-faq.svg'),
        "dependencies": str(ACTION_PATH / 'help-dependencies.svg'),

    }

    def __init__(self, name):
        super().__init__(self.icon_path[name])
