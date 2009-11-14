# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QWidget

from moneyguru.gui.import_window import ImportWindow as ImportWindowModel
from .import_table import ImportTable
from ui.import_window_ui import Ui_ImportWindow

class ImportWindow(QWidget, Ui_ImportWindow):
    def __init__(self, doc):
        QWidget.__init__(self, None)
        self._setupUi()
        self.doc = doc
        self.model = ImportWindowModel(view=self, document=doc.model)
        self.table = ImportTable(dataSource=self.model, view=self.tableView)
        self.table.model.connect()
        self._setupColumns() # Can only be done after the model has been connected
        
        self.tabView.tabCloseRequested.connect(self.tabCloseRequested)
        self.tabView.currentChanged.connect(self.currentTabChanged)
        self.importButton.clicked.connect(self.importClicked)
    
    def _setupUi(self):
        self.setupUi(self)
        self.tabView.setTabsClosable(True)
        self.tabView.setDrawBase(False)
        self.tabView.setDocumentMode(True)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setHighlightSections(False)
        h.resizeSection(0, 28)
    
    #--- Event Handlers
    def currentTabChanged(self, index):
        self.model.selected_pane_index = index
    
    def importClicked(self):
        self.model.import_selected_pane()
    
    def tabCloseRequested(self, index):
        self.model.close_pane(index)
        self.tabView.removeTab(index)
    
    #--- model --> view
    def close(self):
        self.hide()
    
    def close_selected_tab(self):
        self.tabView.removeTab(self.tabView.currentIndex())
    
    def refresh(self):
        while self.tabView.count():
            self.tabView.removeTab(0)
        for pane in self.model.panes:
            self.tabView.addTab(pane.name)
    
    def update_selected_pane(self):
        index = self.model.selected_pane_index
        if index != self.tabView.currentIndex(): # this prevents infinite loops
            self.tabView.setCurrentIndex(index)
    
