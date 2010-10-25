# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPixmap

from qtlib.column import Column
from core.gui.entry_table import EntryTable as EntryTableModel
from core.trans import tr
from ...support.item_delegate import ItemDecoration
from ..table import TableDelegate, DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT
from ..table_with_transactions import TableWithTransactions

class EntryTableDelegate(TableDelegate):
    def __init__(self, model, columns):
        TableDelegate.__init__(self, model, columns)
        arrow = QPixmap(':/right_arrow_gray_12')
        arrowSelected = QPixmap(':/right_arrow_white_12')
        self._decoArrow = ItemDecoration(arrow, self._model.show_transfer_account)
        self._decoArrowSelected = ItemDecoration(arrowSelected, self._model.show_transfer_account)
    
    def _get_decorations(self, index, isSelected):
        column = self._columns[index.column()]
        if column.attrname == 'transfer':
            return [self._decoArrowSelected if isSelected else self._decoArrow]
        else:
            return []
    

class EntryTable(TableWithTransactions):
    COLUMNS = [
        Column('status', '', 25, cantTruncate=True),
        Column('date', tr('Date'), 86, editor=DATE_EDIT, cantTruncate=True),
        Column('reconciliation_date', tr('Reconciliation Date'), 110, editor=DATE_EDIT, cantTruncate=True),
        Column('description', tr('Description'), 150, editor=DESCRIPTION_EDIT),
        Column('payee', tr('Payee'), 150, editor=PAYEE_EDIT),
        Column('checkno', tr('Check #'), 100),
        Column('transfer', tr('Transfer'), 120, editor=ACCOUNT_EDIT),
        Column('increase', tr('Increase'), 95, alignment=Qt.AlignRight, cantTruncate=True),
        Column('decrease', tr('Decrease'), 95, alignment=Qt.AlignRight, cantTruncate=True),
        Column('debit', tr('Debit'), 95, alignment=Qt.AlignRight, cantTruncate=True),
        Column('credit', tr('Credit'), 95, alignment=Qt.AlignRight, cantTruncate=True),
        Column('balance', tr('Balance'), 110, alignment=Qt.AlignRight, cantTruncate=True),
    ]
    
    def __init__(self, account_view, view):
        model = EntryTableModel(view=self, account_view=account_view.model)
        TableWithTransactions.__init__(self, model, view)
        self.tableDelegate = EntryTableDelegate(self.model, self.COLUMNS)
        self.view.setItemDelegate(self.tableDelegate)
        self.view.sortByColumn(1, Qt.AscendingOrder) # sorted by date by default
        self.view.clicked.connect(self.cellClicked)
        self.view.spacePressed.connect(self.model.toggle_reconciled)
        self.view.deletePressed.connect(self.model.delete)
    
    #--- Data methods override
    def _getStatusData(self, row, role):
        # DecorationRole is handled in TableWithTransactions
        if role == Qt.CheckStateRole:
            if row.can_reconcile():
                return Qt.Checked if row.reconciled else Qt.Unchecked
            else:
                return None
        else:
            return TableWithTransactions._getStatusData(self, row, role)
    
    def _getFlags(self, row, column):
        flags = TableWithTransactions._getFlags(self, row, column)
        if column.attrname == 'status':
            if row.can_reconcile() and not row.reconciled:
                flags |= Qt.ItemIsUserCheckable
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
    
