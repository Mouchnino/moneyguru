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
from .table import Table

class EntryTable(Table):
    HEADER = ['', 'Date', 'Description', 'Transfer', 'Increase', 'Decrease', 'Balance']
    ROWATTRS = ['status', 'date', 'description', 'transfer', 'increase', 'decrease', 'balance']
    DATECOLUMNS = frozenset(['date'])
    
    def __init__(self, doc, view):
        model = EntryTableModel(view=self, document=doc.model)
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
    
