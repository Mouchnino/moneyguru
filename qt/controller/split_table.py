# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt

from core.gui.split_table import SplitTable as SplitTableModel
from .column import Column, ACCOUNT_EDIT
from .table import Table

class SplitTable(Table):
    COLUMNS = [
        Column('account', 'Account', 88, editor=ACCOUNT_EDIT),
        Column('memo', 'Memo', 70),
        Column('debit', 'Debit', 70, alignment=Qt.AlignRight),
        Column('credit', 'Credit', 70, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, transactionPanel, view):
        model = SplitTableModel(view=self, transaction_panel=transactionPanel.model)
        Table.__init__(self, model, view)
        self.setColumnsWidth(None)
    

