# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMainWindow, QFileDialog

from moneyguru.gui.main_window import MainWindow as MainWindowModel

from ui.main_window_ui import Ui_MainWindow

from .transaction_view import TransactionView

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, doc):
        QMainWindow.__init__(self, None)
        self.doc = doc
        self.tview = TransactionView(doc=doc)
        children = [None, None, self.tview.ttable.model, None, None, None, None, None, None, None,
            None]
        self.model = MainWindowModel(view=self, document=doc.model, children=children)
        self._setupUi()
        self.model.select_transaction_table()
        
        # Actions
        self.connect(self.actionLoadFile, SIGNAL('triggered()'), self.loadFileTriggered)
    
    def _setupUi(self):
        self.setupUi(self)
        self.mainView.addWidget(self.tview)
    
    #--- Actions
    def loadFileTriggered(self):
        title = "Select a document to load"
        docpath = unicode(QFileDialog.getOpenFileName(self, title))
        if docpath:
            self.doc.model.load_from_xml(docpath)
    
    #--- model --> view
    def show_transaction_table(self):
        self.mainView.currentWidget().disconnect()
        self.mainView.setCurrentIndex(0)
        self.mainView.currentWidget().connect()
    
