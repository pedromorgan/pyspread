#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 19:15:35 2018

@author: mn
"""

from PyQt5.QtWidgets import QAction

from icons import Icon


class Action(QAction):
    """Base class for all actions in pyspread

    Note: Parameter order has changed comparing with QAction

    """

    def __init__(self, parent, label, *connects,
                 icon=None, shortcut=None, statustip=None):
        if icon is None:
            super().__init__(label, parent)
        else:
            super().__init__(icon, label, parent)

        if shortcut is not None:
            self.setShortcut(shortcut)

        if statustip is not None:
            self.setStatusTip(statustip)

        for connect in connects:
            self.triggered.connect(connect)


class MainWindowActions(dict):
    """Holds all QActions for pyspread"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self._add_file_actions()
        self._add_edit_actions()
        self._add_view_actions()
        self._add_format_actions()
        self._add_macro_actions()
        self._add_help_actions()

    def _add_file_actions(self):
        """Adds actions for File menu"""

        self["new"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["open"] = Action(self.parent, "&Open", self.parent.close,
                              icon=Icon("open"),
                              statustip='Open spreadsheet from file')

        self["save"] = Action(self.parent, "&Save", self.parent.close,
                              icon=Icon("save"),
                              shortcut='Ctrl+s',
                              statustip='Save spreadsheet')

        self["save_as"] = Action(self.parent, "Save &As", self.parent.close,
                                 icon=Icon("save_as"),
                                 shortcut='Shift+Ctrl+s',
                                 statustip='Save spreadsheet to a new file')

        self["import"] = Action(self.parent, "&Import", self.parent.close,
                                statustip='Import a file and paste it into '
                                          'the current grid')

        self["export"] = Action(self.parent, "&Export", self.parent.close,
                                statustip="Export selection to a file")

        self["approve"] = Action(self.parent, "&Approve file",
                                 self.parent.close,
                                 icon=Icon("approve"),
                                 statustip='Approve, unfreeze and sign the '
                                           'current file')

        self["clear_globals"] = Action(self.parent, "&Clear globals",
                                       self.parent.close,
                                       icon=Icon("clear_globals"),
                                       statustip='Deletes global variables '
                                                 'from memory and reloads '
                                                 'base modules')

        self["page_setup"] = Action(self.parent, "Page setup",
                                    self.parent.close,
                                    statustip='Setup printer page')

        self["print_preview"] = Action(self.parent, "Print preview",
                                       self.parent.close,
                                       icon=Icon("print_preview"),
                                       statustip='Print preview')

        self["print"] = Action(self.parent, "Print", self.parent.close,
                               icon=Icon("print"),
                               shortcut='Ctrl+p',
                               statustip='Print current spreadsheet')

        self["preferences"] = Action(self.parent, "Preferences...",
                                     self.parent.close,
                                     icon=Icon("preferences"),
                                     statustip='Pyspread setup parameters')

        self["new_gpg_key"] = Action(self.parent, "Switch GPG key...",
                                     self.parent.close,
                                     icon=Icon("new_gpg_key"),
                                     statustip='Create or choose a GPG key '
                                               'pair for signing and '
                                               'verifying pyspread files')

        self["quit"] = Action(self.parent, "&Quit", self.parent.close,
                              icon=Icon("quit"),
                              shortcut='Ctrl+Q',
                              statustip='Exit pyspread')

    def _add_edit_actions(self):
        """Adds actions for Edit menu"""

        self["undo"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["redo"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["cut"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["copy"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["copy_results"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["paste"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["paste_as"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["select_all"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["find"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["replace"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["quote"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["sort_ascending"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["sort_decending"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["insert_rows"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["insert_columns"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["insert_table"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["delete_rows"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["delete_columns"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["delete_table"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["resize_grid"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

    def _add_view_actions(self):
        """Adds actions for View menu"""

        self["fullscreen"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_main_toolbar"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_macro_toolbar"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_widget_toolbar"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_format_toolbar"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_find_toolbar"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["toggle_entryline"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_tablelist"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_macropanel"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["goto_cell"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["check_spelling"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["zoom_in"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["zoom_out"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["zoom_1"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["zoom_fit"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["refresh_cells"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["toggle_periodic_updates"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["show_frozen"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

    def _add_format_actions(self):
        """Adds actions for Format menu"""

        self["copy_format"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["paste_format"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["font"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["bold"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["italics"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["underline"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["strikethrough"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["text_color"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["background_color"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["markup"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["justify_left"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["justify_center"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["justify_right"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["align_top"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["align_center"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["align_bottom"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["rotate_0"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["rotate_90"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["rotate_180"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["rotate_270"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["freeze_cell"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["lock_cell"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["merge_cells"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

    def _add_macro_actions(self):
        """Adds actions for Macro menu"""

        self["load_macros"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["save_macros"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["insert_bitmap"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["link_bitmap"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["insert_chart"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

    def _add_help_actions(self):
        """Adds actions for Help menu"""

        self["first_steps"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["tutorial"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["faq"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')


        self["dependencies"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')

        self["about"] = Action(self.parent, "&New", self.parent.close,
                             icon=Icon("new"),
                             shortcut='Ctrl+n',
                             statustip='Create a new, empty spreadsheet')
