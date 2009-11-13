# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.split_table import SplitTable as SplitTableModel
from .table import Table

class SplitTable(Table):
    HEADER = ['Account', 'Memo', 'Debit', 'Credit']
    ROWATTRS = ['account', 'memo', 'debit', 'credit']
    
    def _getModel(self):
        return SplitTableModel(view=self, transaction_panel=self.dataSource)
    
