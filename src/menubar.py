#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 15:12:28 2018

@author: mn
"""

from PyQt5.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    """The main menubar for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self._create_menu(main_window.actions)

    def _create_menu(self, actions):
        """Fills the main menu with QActions"""

        fileMenu = self.addMenu('&File')

        fileMenu.addAction(actions["new"])
        fileMenu.addAction(actions["open"])
        fileMenu.addAction(actions["save"])
        fileMenu.addAction(actions["save_as"])
        fileMenu.addAction(actions["import"])
        fileMenu.addAction(actions["export"])
        fileMenu.addAction(actions["approve"])
        fileMenu.addAction(actions["clear_globals"])
        fileMenu.addAction(actions["page_setup"])
        fileMenu.addAction(actions["print_preview"])
        fileMenu.addAction(actions["print"])
        fileMenu.addAction(actions["preferences"])
        fileMenu.addAction(actions["new_gpg_key"])
        fileMenu.addAction(actions["quit"])
