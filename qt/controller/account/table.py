# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt

from moneyguru.gui.entry_table import EntryTable as EntryTableModel
from ..column import Column, DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT
from ..table_with_transactions import TableWithTransactions

class EntryTable(TableWithTransactions):
    COLUMNS = [
        Column('status', '', 25),
        Column('date', 'Date', 87, editor=DATE_EDIT),
        Column('description', 'Description', 150, editor=DESCRIPTION_EDIT),
        Column('payee', 'Payee', 150, editor=PAYEE_EDIT),
        Column('checkno', 'Check #', 100),
        Column('transfer', 'Transfer', 120, editor=ACCOUNT_EDIT),
        Column('increase', 'Increase', 95, alignment=Qt.AlignRight),
        Column('decrease', 'Decrease', 95, alignment=Qt.AlignRight),
        Column('balance', 'Balance', 110, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, doc, view, totalsLabel):
        model = EntryTableModel(view=self, document=doc.model)
        TableWithTransactions.__init__(self, model, view)
        self.totalsLabel = totalsLabel
        self.view.clicked.connect(self.cellClicked)
        self.view.horizontalHeader().sectionMoved.connect(self.headerSectionMoved)
        self.view.spacePressed.connect(self.model.toggle_reconciled)
        self.view.deletePressed.connect(self.model.delete)
    
    #--- ColumnBearer override
    def setHiddenColumns(self, hiddenColumns):
        TableWithTransactions.setHiddenColumns(self, hiddenColumns)
        self.model.change_columns(self.visibleRowAttrs())
    
    #--- Data methods override
    def _getStatusData(self, row, role):
        # DecorationRole is handled in TableWithTransactions
        if role == Qt.CheckStateRole:
            if row.can_reconcile() and not row.reconciled:
                return Qt.Checked if row.reconciliation_pending else Qt.Unchecked
            else:
                return None
        else:
            return TableWithTransactions._getStatusData(self, row, role)
    
    def _getFlags(self, row, column):
        flags = TableWithTransactions._getFlags(self, row, column)
        if column.attrname == 'status':
            if row.can_reconcile() and not row.reconciled:
                flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags
    
    def _setData(self, row, column, value, role):
        if column.attrname == 'status':
            if role == Qt.CheckStateRole:
                row.toggle_reconciled()
                return True
            else:
                return False
        else:
            return TableWithTransactions._setData(self, row, column, value, role)
    
    #--- Event Handling
    def cellClicked(self, index):
        rowattr = self.COLUMNS[index.column()].attrname
        if rowattr == 'status':
            row = self.model[index.row()]
            if row.can_reconcile() and row.reconciled:
                row.toggle_reconciled()
    
    def headerSectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        self.model.change_columns(self.visibleRowAttrs())
    
    #--- model --> view
    def refresh(self):
        TableWithTransactions.refresh(self)
        self.totalsLabel.setText(self.model.totals)
        balanceColumn = self.ATTR2COLUMN['balance']
        shouldShow = self.model.should_show_balance_column()
        self._headerView.setSectionHidden(balanceColumn.index, not shouldShow)
    
