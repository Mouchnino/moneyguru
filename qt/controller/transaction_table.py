# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.transaction_table import TransactionTable as TransactionTableModel
from .table import Table

class TransactionTable(Table):
    HEADER = ['Date', 'Description', 'From', 'To', 'Amount']
    ROWATTRS = ['date', 'description', 'from_', 'to', 'amount']
    DATECOLUMNS = frozenset(['date'])
    
    def __init__(self, doc, view):
        model = TransactionTableModel(view=self, document=doc.model)
        Table.__init__(self, model, view)
    
