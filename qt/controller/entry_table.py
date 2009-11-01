# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.entry_table import EntryTable as EntryTableModel
from .table import Table

class EntryTable(Table):
    HEADER = ['Date', 'Description', 'Transfer', 'Increase', 'Decrease', 'Balance']
    ROWATTRS = ['date', 'description', 'transfer', 'increase', 'decrease', 'balance']
    
    def _getModel(self):
        return EntryTableModel(view=self, document=self.doc.model)
    
