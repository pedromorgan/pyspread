#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 19:58:58 2018

@author: mn
"""

from PyQt5.QtWidgets import QToolBar


class ToolBar(QToolBar):
    """The main toolbar for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self._create_toolbar(main_window.actions)

    def _create_toolbar(self, actions):
        """Fills the main toolbar with QActions"""

        self.addAction(actions["new"])
        self.addAction(actions["open"])
        self.addAction(actions["save"])

