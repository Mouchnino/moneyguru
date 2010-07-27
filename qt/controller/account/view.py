# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.account_view import AccountView as AccountViewModel
from core.trans import tr

from ..base_view import BaseView
from .filter_bar import EntryFilterBar
from .table import EntryTable
from .bar_graph import AccountBarGraph
from .line_graph import AccountLineGraph
from ui.entry_view_ui import Ui_EntryView

class EntryView(BaseView, Ui_EntryView):
    PRINT_TITLE_FORMAT = tr("Entries from {startDate} to {endDate}")
    
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.mainwindow = mainwindow
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = AccountViewModel(view=self, mainwindow=mainwindow.model)
        self.etable = EntryTable(self, view=self.tableView)
        self.efbar = EntryFilterBar(self, view=self.filterBar)
        self.bgraph = AccountBarGraph(self, view=self.barGraphView)
        self.lgraph = AccountLineGraph(self, view=self.lineGraphView)
        children = [self.etable.model, self.lgraph.model, self.bgraph.model, self.efbar.model]
        self.model.set_children(children)
        self._setupColumns() # Can only be done after the model has been connected
        
        self.reconciliationButton.clicked.connect(self.model.toggle_reconciliation_mode)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.etable.setColumnsWidth()
        self.etable.setColumnsOrder()
    
    #--- QWidget override
    def setFocus(self):
        self.etable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.etable)
        viewPrinter.fit(self.graphView.currentWidget(), 300, 150, expandH=True, expandV=True)
    
    def updateOptionalWidgetsVisibility(self):
        prefs = self.doc.app.prefs
        self.etable.setHiddenColumns(prefs.entryHiddenColumns)
        self.graphView.setHidden(not prefs.entryGraphVisible)
    
    #--- model --> view
    def refresh_reconciliation_button(self):
        if self.model.can_toggle_reconciliation_mode:
            self.reconciliationButton.setEnabled(True)
            self.reconciliationButton.setChecked(self.model.reconciliation_mode)
        else:
            self.reconciliationButton.setEnabled(False)
            self.reconciliationButton.setChecked(False)
    
    def show_bar_graph(self):
        self.graphView.setCurrentIndex(1)
    
    def show_line_graph(self):
        self.graphView.setCurrentIndex(0)
    
