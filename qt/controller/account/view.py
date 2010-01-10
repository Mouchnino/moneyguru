# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.account_view import AccountView as AccountViewModel

from ..base_view import BaseView
from .filter_bar import EntryFilterBar
from .table import EntryTable
from .bar_graph import AccountBarGraph
from .line_graph import AccountLineGraph
from ui.entry_view_ui import Ui_EntryView

class EntryView(BaseView, Ui_EntryView):
    PRINT_TITLE_FORMAT = "Entries from {startDate} to {endDate}"
    
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.etable = EntryTable(doc=doc, view=self.tableView)
        self.efbar = EntryFilterBar(doc=doc, view=self.filterBar)
        self.bgraph = AccountBarGraph(doc=doc, view=self.barGraphView)
        self.lgraph = AccountLineGraph(doc=doc, view=self.lineGraphView)
        children = [self.etable.model, self.lgraph.model, self.bgraph.model, self.efbar.model]
        self.model = AccountViewModel(view=self, document=doc.model, children=children)
        self._setupColumns() # Can only be done after the model has been connected
        
        self.doc.app.willSavePrefs.connect(self._savePrefs)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.etable.setColumnsWidth(self.doc.app.prefs.entryColumnWidths)
        self.etable.setColumnsOrder(self.doc.app.prefs.entryColumnOrder)
    
    def _savePrefs(self):
        h = self.tableView.horizontalHeader()
        widths = [h.sectionSize(index) for index in xrange(len(self.etable.COLUMNS))]
        self.doc.app.prefs.entryColumnWidths = widths
        order = [h.logicalIndex(index) for index in xrange(len(self.etable.COLUMNS))]
        self.doc.app.prefs.entryColumnOrder = order
    
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
    def refresh_totals(self):
        self.totalsLabel.setText(self.model.totals)
    
    def show_bar_graph(self):
        self.graphView.setCurrentIndex(1)
    
    def show_line_graph(self):
        self.graphView.setCurrentIndex(0)
    
