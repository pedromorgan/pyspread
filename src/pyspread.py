#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Pyspread QT transition tryout

"""

import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QApplication
from icons import Icon

from menubar import MenuBar
from toolbar import ToolBar
from actions import MainWindowActions


class MainWindow(QMainWindow):
    """Pyspread main window"""

    def __init__(self):
        super().__init__()

        self.actions = MainWindowActions(self)
        self.initUI()

    def initUI(self):

        self.setWindowIcon(Icon("pyspread"))

        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)

        self.statusBar()
        self.setMenuBar(MenuBar(self))
        self.addToolBar(ToolBar(self))

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Pyspread')
        self.show()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
