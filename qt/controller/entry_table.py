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
from PyQt4.QtGui import QPixmap

from moneyguru.gui.entry_table import EntryTable as EntryTableModel
from .table import Table, DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT
from .table_with_transactions import TableWithTransactions

class EntryTable(TableWithTransactions):
    HEADER = ['', 'Date', 'Description', 'Payee', 'Check #', 'Transfer', 'Increase', 'Decrease', 'Balance']
    ROWATTRS = ['status', 'date', 'description', 'payee', 'checkno', 'transfer', 'increase', 'decrease', 'balance']
    SPECIAL_COLUMNS = {
        'date': DATE_EDIT,
        'description': DESCRIPTION_EDIT,
        'transfer': ACCOUNT_EDIT,
    }
    
    def __init__(self, doc, view):
        model = EntryTableModel(view=self, document=doc.model)
        TableWithTransactions.__init__(self, model, view)
        self.view.clicked.connect(self.cellClicked)
    
    #--- Data methods override
    def _getData(self, row, rowattr, role):
        if rowattr == 'status':
            if role == Qt.DecorationRole:
                if row.reconciled:
                    return QPixmap(':/check_16')
                elif row.is_budget:
                    return QPixmap(':/budget_16')
                elif row.recurrent:
                    return QPixmap(':/recurrent_16')
                else:
                    return None
            elif (role == Qt.CheckStateRole) and row.can_reconcile() and not row.reconciled:
                return Qt.Checked if row.reconciliation_pending else Qt.Unchecked
            else:
                return None
        else:
            return TableWithTransactions._getData(self, row, rowattr, role)
    
    def _getFlags(self, row, rowattr):
        flags = TableWithTransactions._getFlags(self, row, rowattr)
        if rowattr == 'status':
            if row.can_reconcile() and not row.reconciled:
                flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags
    
    def _setData(self, row, rowattr, value, role):
        if rowattr == 'status':
            if role == Qt.CheckStateRole:
                row.toggle_reconciled()
                return True
            else:
                return False
        else:
            return TableWithTransactions._setData(self, row, rowattr, value, role)
    
    #--- Event Handling
    def cellClicked(self, index):
        rowattr = self.ROWATTRS[index.column()]
        if rowattr == 'status':
            row = self.model[index.row()]
            if row.can_reconcile() and row.reconciled:
                row.toggle_reconciled()
    
