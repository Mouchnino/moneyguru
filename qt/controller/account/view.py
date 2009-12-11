# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

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
        self.etable = EntryTable(doc=doc, view=self.tableView, totalsLabel=self.totalsLabel)
        self.efbar = EntryFilterBar(doc=doc, view=self.filterBar)
        self.bgraph = AccountBarGraph(doc=doc, view=self.barGraphView)
        self.lgraph = AccountLineGraph(doc=doc, view=self.lineGraphView)
        # We don't add the graphs to self.children because connection/disconnection occur separately for them
        self.children = [self.etable, self.efbar]
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
    
    def showBarGraph(self):
        self.lgraph.model.disconnect()
        self.bgraph.model.connect()
        self.graphView.setCurrentIndex(1)
    
    def showLineGraph(self):
        self.bgraph.model.disconnect()
        self.lgraph.model.connect()
        self.graphView.setCurrentIndex(0)
    
    def updateOptionalWidgetsVisibility(self):
        prefs = self.doc.app.prefs
        self.etable.setHiddenColumns(prefs.entryHiddenColumns)
        self.graphView.setHidden(not prefs.entryGraphVisible)
    