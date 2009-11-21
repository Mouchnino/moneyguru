# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.budget_table import BudgetTable as BudgetTableModel
from .table import Table

class BudgetTable(Table):
    HEADER = ['Start Date', 'Stop Date', 'Repeat Type', 'Interval', 'Account', 'Target', 'Amount']
    ROWATTRS = ['start_date', 'stop_date', 'repeat_type', 'interval', 'account', 'target', 'amount']
    
    def __init__(self, doc, view):
        model = BudgetTableModel(view=self, document=doc.model)
        Table.__init__(self, model, view)
    
