# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt

from core.gui.income_statement import IncomeStatement as IncomeStatementModel
from ..account_sheet import AccountSheet, AccountSheetDelegate
from ..column import Column

class ProfitSheet(AccountSheet):
    COLUMNS = [
        Column('name', 'Account', 133),
        Column('account_number', 'Account #', 80),
        Column('cash_flow', 'Current', 100, alignment=Qt.AlignRight),
        Column('last_cash_flow', 'Last', 100, alignment=Qt.AlignRight),
        Column('delta', 'Change', 100, alignment=Qt.AlignRight),
        Column('delta_perc', 'Change %', 100),
        Column('budgeted', 'Budgeted', 100, alignment=Qt.AlignRight),
    ]
    EXPANDED_NODE_PREF_NAME = 'profitLossExpandedPaths'
    AMOUNT_ATTRS = set(['cash_flow', 'last_cash_flow', 'delta', 'delta_perc', 'budgeted'])
    BOLD_ATTRS = set(['cash_flow'])
    
    def __init__(self, doc, view):
        model = IncomeStatementModel(view=self, document=doc.model)
        AccountSheet.__init__(self, doc, model, view)
    
