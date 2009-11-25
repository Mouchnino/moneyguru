# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base_view import BaseView
from .transaction_table import TransactionTable
from ui.transaction_view_ui import Ui_TransactionView

class TransactionView(BaseView, Ui_TransactionView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.ttable = TransactionTable(doc=doc, view=self.tableView)
        self.children = [self.ttable]
        self._setupColumns() # Can only be done after the model has been connected
        
        self.doc.app.willSavePrefs.connect(self._savePrefs)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.ttable.setColumnsWidth(self.doc.app.prefs.transactionColumnWidths)
        self.ttable.setColumnsOrder(self.doc.app.prefs.transactionColumnOrder)
    
    def _savePrefs(self):
        h = self.tableView.horizontalHeader()
        widths = [h.sectionSize(index) for index in xrange(len(self.ttable.COLUMNS))]
        self.doc.app.prefs.transactionColumnWidths = widths
        order = [h.visualIndex(index) for index in xrange(len(self.ttable.COLUMNS))]
        self.doc.app.prefs.transactionColumnOrder = order
    
    #--- Public
    def updateOptionalWidgetsVisibility(self):
        prefs = self.doc.app.prefs
        h = self.tableView.horizontalHeader()
        for column in self.ttable.COLUMNS:
            isHidden = column.attrname in prefs.transactionHiddenColumns
            h.setSectionHidden(column.index, isHidden)
    
