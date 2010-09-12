# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFont, QBrush, QColor

from qtlib.column import Column
from core.gui.general_ledger_table import GeneralLedgerTable as GeneralLedgerTableModel
from core.trans import tr
from const import EXTRA_ROLE, EXTRA_SPAN_ALL_COLUMNS
from ..table import DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT
from ..table_with_transactions import TableWithTransactions

class GeneralLedgerTable(TableWithTransactions):
    COLUMNS = [
        Column('status', '', 25, cantTruncate=True),
        Column('date', tr('Date'), 86, editor=DATE_EDIT, cantTruncate=True),
        Column('reconciliation_date', tr('Reconciliation Date'), 110, editor=DATE_EDIT, cantTruncate=True),
        Column('description', tr('Description'), 150, editor=DESCRIPTION_EDIT),
        Column('payee', tr('Payee'), 150, editor=PAYEE_EDIT),
        Column('checkno', tr('Check #'), 100),
        Column('transfer', tr('Transfer'), 120, editor=ACCOUNT_EDIT),
        Column('debit', tr('Debit'), 95, alignment=Qt.AlignRight, cantTruncate=True),
        Column('credit', tr('Credit'), 95, alignment=Qt.AlignRight, cantTruncate=True),
        Column('balance', tr('Balance'), 110, alignment=Qt.AlignRight, cantTruncate=True),
    ]
    
    def __init__(self, general_ledger_view, view):
        model = GeneralLedgerTableModel(view=self, parent_view=general_ledger_view.model)
        TableWithTransactions.__init__(self, model, view)
        self.view.deletePressed.connect(self.model.delete)
    
    #--- Override
    def _getData(self, row, column, role):
        is_account_row = self.model.is_account_row(row)
        if role == EXTRA_ROLE:
            flags = 0
            if is_account_row:
                flags |= EXTRA_SPAN_ALL_COLUMNS
            return flags
        elif is_account_row:
            if role == Qt.DisplayRole:
                return row.account_name
            elif role == Qt.FontRole:
                font = QFont(self.view.font())
                font.setBold(True)
                return font
            elif role == Qt.BackgroundRole:
                return QBrush(QColor(Qt.lightGray))
        elif role == Qt.FontRole:
            font = QFont(self.view.font())
            is_bold = self.model.is_bold_row(row)
            font.setBold(is_bold)
            return font
        else:
            return TableWithTransactions._getData(self, row, column, role)
    
    def reset(self):
        TableWithTransactions.reset(self)
        self.view.clearSpans()
        for index, row in enumerate(self.model):
            if self.model.is_account_row(row):
                self.view.setSpan(index, 0, 1, len(self.COLUMNS))
    
