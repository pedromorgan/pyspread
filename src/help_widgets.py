# -*- coding: utf-8 -*-

import os
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import pyqtSignal, Qt

import mistune

from icons import Icon

ROOT_DIR = os.path.abspath( os.path.join(os.path.dirname( __file__ ), "..") )
HELP_DOCS_DIR = os.path.join(ROOT_DIR, "docs", "help")
HELP_TEMPLATES_DIR = os.path.join(ROOT_DIR, "docs", "_templates")


class C:
    """Table columns"""
    node = 0
    page = 1

class HelpDialog( QtWidgets.QDialog ):


    def __init__( self, page=None ):
        super().__init__()

        self.setWindowTitle("Help")
        self.setWindowIcon(Icon("help"))

        # self.setWindowFlags(QtCore.Qt.Popup)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setMinimumWidth(900)
        self.setMinimumHeight(700)


        m = 0
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(m, m, m, m)
        self.setLayout(mainLayout)


        self.splitter = QtWidgets.QSplitter()
        mainLayout.addWidget(self.splitter, 100)

        ## Contents Tree
        self.tree = QtWidgets.QTreeWidget()
        self.splitter.addWidget(self.tree)
        hi = self.tree.headerItem()
        hi.setText(C.node, "File")
        hi.setText(C.page, "Page")
        self.tree.header().hide()

        self.tree.setColumnHidden(C.page, True)
        self.tree.header().setStretchLastSection(True)
        self.tree.setUniformRowHeights(True)

        self.tree.setFixedWidth(200)
        self.tree.itemSelectionChanged.connect(self.on_tree_selection)


        ## Tab Widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.splitter.addWidget(self.tabWidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        self.load_content_tree()

        if page:
            self.load_page(page)

    def load_content_tree(self):

        self.tree.clear()
        self.tree.setUpdatesEnabled(False)


        item = QtWidgets.QTreeWidgetItem()
        item.setText(C.node, "Index")
        #item.setIcon(C.node, Icon("help"))
        item.setText(C.page, "index.md" )
        self.tree.addTopLevelItem(item)

        rootNode = self.tree.invisibleRootItem()
        self.load_dir_node(rootNode, HELP_DOCS_DIR)

        self.tree.setUpdatesEnabled(True)

    def load_dir_node(self, pItem, pth):

        files = os.listdir(pth)

        for f in sorted(files):
            xpth = os.path.join(pth, f)[len(HELP_DOCS_DIR) + 1:]

            if f == "index.md" and pth == HELP_DOCS_DIR:
                continue

            if os.path.isdir(f):
                item = QtWidgets.QTreeWidgetItem(pItem)
                item.setText(C.node, f)
                #item.setIcon(C.node,) Folder
                item.setText(C.page, xpth )

                self.load_dir_node(item, os.path.join(pth, f))
                item.setExpanded(True)

            elif f.endswith(".md"):
                item = QtWidgets.QTreeWidgetItem(pItem)
                item.setText(C.node, self.title_from_filename(f))
                item.setText(C.page, xpth )

    def title_from_filename(self, fn):
        fn = os.path.basename(fn)
        if fn.endswith(".md"):
            fn = fn[0:-3]
        return fn.replace("_", " ").title()

    def select_page(self, page):
        idx = None
        if self.tabWidget.count() == 0:
            return idx

        ## check page is aleady loaded, and select
        for i in range(0, self.tabWidget.count()):

            if self.tabWidget.widget(i).page == page:
                self.tabWidget.blockSignals(True)
                self.tabWidget.setCurrentIndex(i)
                self.tabWidget.blockSignals(False)
                idx = i
                break
        items = self.tree.findItems(page, Qt.MatchExactly|Qt.MatchRecursive, C.page)
        if len(items) > 0:
            self.tree.blockSignals(True)
            self.tree.setCurrentItem(items[0])
            self.tree.blockSignals(False)
        return idx



    def load_page(self, page):


        full_path = os.path.join(HELP_DOCS_DIR, page)
        if os.path.isdir(full_path):
            return

        elif not page.endswith(".md"):
            full_path = full_path + ".md"


        idx = self.select_page(page)
        if idx != None:
            return

        if not os.path.exists(full_path):
            return

        html_tpl = ""
        with open(os.path.join(HELP_TEMPLATES_DIR, "embeded_markdown.html"), "r") as f:
            html_tpl = f.read()
            f.close()


        md_text = ""
        with open(full_path, "r") as f:
            md_text = f.read()
            f.close()

        html = mistune.markdown(md_text, escape=False)
        out_html = html_tpl.replace("##++CONTENT++##", html)



        self.tabWidget.blockSignals(True)
        webView = HelpPageView()
        nidx = self.tabWidget.addTab(webView, self.title_from_filename(page))
        webView.set_data(page, out_html )


        webView.sigPageLinkClicked.connect(self.load_page)

        self.tabWidget.setCurrentIndex(nidx)
        self.select_tree_node(page)
        self.tabWidget.blockSignals(False)




    def on_tree_selection(self):
        item = self.tree.currentItem()
        if item == None:
            return
        self.load_page( item.text(C.page) )


    def on_tab_close_requested(self, idx):
        self.tabWidget.removeTab(idx)

    def on_tab_changed(self, nidx):
        if nidx == -1:
            self.tree.blockSignals(True)
            self.tree.clearSelection()
            self.tree.blockSignals(False)
            return
        page = self.tabWidget.widget(nidx).page
        self.select_tree_node(page)

    def select_tree_node(self, page, block=True):

        self.tree.blockSignals(True)
        items = self.tree.findItems(page, Qt.MatchExactly|Qt.MatchRecursive, C.page)
        if len(items) > 0:
            self.tree.setCurrentItem(items[0])
        else:
            # page not in menu
            pass #print ere
        self.tree.blockSignals(False)

class HelpPageView( QtWidgets.QWidget ):

    sigPageLinkClicked = pyqtSignal(str)

    def __init__( self, parent=None, page=None):
        QtWidgets.QWidget.__init__( self, parent )

        self.debug = True
        self.page = None

        lay = QtWidgets.QVBoxLayout()
        lay.setSpacing(0)
        lay.setContentsMargins(0,0,0,0)
        self.setLayout(lay)

        self.webView = QtWebEngineWidgets.QWebEngineView()
        lay.addWidget(self.webView, 2)

    def set_data(self, page, html ):
        self.page = page
        baseu = os.path.join(HELP_DOCS_DIR, "help")
        base_url = QtCore.QUrl.fromLocalFile( baseu ) # TODO

        self.webView.setHtml(html, base_url)

    def on_link_clicked(self, url):

        page = str(url.path())[1:]
        self.sigPageLinkClicked.emit( page )
