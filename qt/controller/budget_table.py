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
from .column import Column
from .table import Table

class BudgetTable(Table):
    COLUMNS = [
        Column('start_date', 'Start Date', 120),
        Column('stop_date', 'Stop Date', 120),
        Column('repeat_type', 'Repeat Type', 120),
        Column('interval', 'Interval', 80),
        Column('account', 'Account', 120),
        Column('target', 'Target', 120),
        Column('amount', 'Amount', 120),
    ]
    
    def __init__(self, doc, view):
        model = BudgetTableModel(view=self, document=doc.model)
        Table.__init__(self, model, view)
    
