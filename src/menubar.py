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

        self.actions = main_window.actions

        self._create_menu()

    def _create_menu(self):
        """Fills the main menu with QActions"""

        self.file_menu = self._get_file_menu()
        self.edit_menu = self._get_edit_menu()
        self.view_menu = self._get_view_menu()
        self.format_menu = self._get_format_menu()
        self.macro_menu = self._get_macro_menu()
        self.help_menu = self._get_help_menu()

    def _get_file_menu(self):
        """Creates the File menu, fills it with QActions and returns it"""

        file_menu = self.addMenu('&File')

        file_menu.addAction(self.actions["new"])
        file_menu.addAction(self.actions["open"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions["save"])
        file_menu.addAction(self.actions["save_as"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions["import"])
        file_menu.addAction(self.actions["export"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions["approve"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions["clear_globals"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions["page_setup"])
        file_menu.addAction(self.actions["print_preview"])
        file_menu.addAction(self.actions["print"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions["preferences"])
        file_menu.addAction(self.actions["new_gpg_key"])
        file_menu.addSeparator()
        file_menu.addAction(self.actions["quit"])

        return file_menu

    def _get_edit_menu(self):
        """Creates the Edit menu, fills it with QActions and returns it"""

        edit_menu = self.addMenu('&Edit')

        edit_menu.addAction(self.actions["undo"])
        edit_menu.addAction(self.actions["redo"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions["cut"])
        edit_menu.addAction(self.actions["copy"])
        edit_menu.addAction(self.actions["copy_results"])
        edit_menu.addAction(self.actions["paste"])
        edit_menu.addAction(self.actions["paste_as"])
        edit_menu.addAction(self.actions["select_all"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions["find"])
        edit_menu.addAction(self.actions["replace"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions["quote"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions["sort_ascending"])
        edit_menu.addAction(self.actions["sort_decending"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions["insert_rows"])
        edit_menu.addAction(self.actions["insert_columns"])
        edit_menu.addAction(self.actions["insert_table"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions["delete_rows"])
        edit_menu.addAction(self.actions["delete_columns"])
        edit_menu.addAction(self.actions["delete_table"])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions["resize_grid"])

        return edit_menu

    def _get_view_menu(self):
        """Creates the View menu, fills it with QActions and returns it"""

        view_menu = self.addMenu('&View')

        view_menu.addAction(self.actions["fullscreen"])
        view_menu.addSeparator()

        toolbar_submenu = view_menu.addMenu('Toolbars')
        toolbar_submenu.addAction(self.actions["toggle_main_toolbar"])
        toolbar_submenu.addAction(self.actions["toggle_macro_toolbar"])
        toolbar_submenu.addAction(self.actions["toggle_widget_toolbar"])
        toolbar_submenu.addAction(self.actions["toggle_format_toolbar"])
        toolbar_submenu.addAction(self.actions["toggle_find_toolbar"])

        view_menu.addAction(self.actions["toggle_entryline"])
        view_menu.addAction(self.actions["toggle_tablelist"])
        view_menu.addAction(self.actions["toggle_macropanel"])
        view_menu.addSeparator()
        view_menu.addAction(self.actions["goto_cell"])
        view_menu.addSeparator()
        view_menu.addAction(self.actions["check_spelling"])
        view_menu.addSeparator()
        view_menu.addAction(self.actions["zoom_in"])
        view_menu.addAction(self.actions["zoom_out"])
        view_menu.addAction(self.actions["zoom_1"])
        view_menu.addAction(self.actions["zoom_fit"])
        view_menu.addSeparator()
        view_menu.addAction(self.actions["refresh_cells"])
        view_menu.addAction(self.actions["toggle_periodic_updates"])
        view_menu.addSeparator()
        view_menu.addAction(self.actions["show_frozen"])

        return view_menu

    def _get_format_menu(self):
        """Creates the Format menu, fills it with QActions and returns it"""

        format_menu = self.addMenu('&Format')

        format_menu.addAction(self.actions["copy_format"])
        format_menu.addAction(self.actions["paste_format"])
        format_menu.addSeparator()
        format_menu.addAction(self.actions["font"])
        format_menu.addAction(self.actions["bold"])
        format_menu.addAction(self.actions["italics"])
        format_menu.addAction(self.actions["underline"])
        format_menu.addAction(self.actions["strikethrough"])
        format_menu.addSeparator()
        format_menu.addAction(self.actions["text_color"])
        format_menu.addAction(self.actions["background_color"])
        format_menu.addSeparator()
        format_menu.addAction(self.actions["markup"])
        format_menu.addSeparator()

        justification_submenu = format_menu.addMenu('Justification')
        justification_submenu.addAction(self.actions["justify_left"])
        justification_submenu.addAction(self.actions["justify_center"])
        justification_submenu.addAction(self.actions["justify_right"])

        alignment_submenu = format_menu.addMenu('Alignment')
        alignment_submenu.addAction(self.actions["align_top"])
        alignment_submenu.addAction(self.actions["align_center"])
        alignment_submenu.addAction(self.actions["align_bottom"])

        rotation_submenu = format_menu.addMenu('Rotation')
        rotation_submenu.addAction(self.actions["rotate_0"])
        rotation_submenu.addAction(self.actions["rotate_90"])
        rotation_submenu.addAction(self.actions["rotate_180"])
        rotation_submenu.addAction(self.actions["rotate_270"])

        format_menu.addSeparator()
        format_menu.addAction(self.actions["freeze_cell"])
        format_menu.addAction(self.actions["lock_cell"])
        format_menu.addAction(self.actions["merge_cells"])

        return format_menu

    def _get_macro_menu(self):
        """Creates the Macro menu, fills it with QActions and returns it"""

        macro_menu = self.addMenu('&Macro')

        macro_menu.addAction(self.actions["load_macros"])
        macro_menu.addAction(self.actions["save_macros"])
        macro_menu.addSeparator()
        macro_menu.addAction(self.actions["insert_bitmap"])
        macro_menu.addAction(self.actions["link_bitmap"])
        macro_menu.addAction(self.actions["insert_chart"])

        return macro_menu

    def _get_help_menu(self):
        """Creates the Help menu, fills it with QActions and returns it"""

        help_menu = self.addMenu('&Help')

        help_menu.addAction(self.actions["first_steps"])
        help_menu.addAction(self.actions["tutorial"])
        help_menu.addAction(self.actions["faq"])
        help_menu.addSeparator()
        help_menu.addAction(self.actions["dependencies"])
        help_menu.addSeparator()
        help_menu.addAction(self.actions["about"])

        return help_menu
