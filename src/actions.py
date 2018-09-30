#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 19:15:35 2018

@author: mn
"""

from PyQt5.QtWidgets import QAction

from icons import Icon


class Action(QAction):
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

    def _add_file_actions(self):
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
