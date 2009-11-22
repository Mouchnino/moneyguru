# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPixmap

from moneyguru.gui.transaction_table import TransactionTable as TransactionTableModel
from .table import Table, DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT

class TransactionTable(Table):
    HEADER = ['', 'Date', 'Description', 'From', 'To', 'Amount']
    ROWATTRS = ['status', 'date', 'description', 'from_', 'to', 'amount']
    SPECIAL_COLUMNS = {
        'date': DATE_EDIT,
        'description': DESCRIPTION_EDIT,
        'from_': ACCOUNT_EDIT,
        'to': ACCOUNT_EDIT,
    }
    
    def __init__(self, doc, view):
        model = TransactionTableModel(view=self, document=doc.model)
        Table.__init__(self, model, view)
    
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
            else:
                return None
        else:
            return Table._getData(self, row, rowattr, role)
    
