# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.income_statement import IncomeStatement as IncomeStatementModel
from ..account_sheet import AccountSheet
from ..column import Column

class ProfitSheet(AccountSheet):
    COLUMNS = [
        Column('name', 'Account', 120),
        Column('cash_flow', 'Current', 100),
        Column('last_cash_flow', 'Last', 100),
        Column('delta', 'Change', 100),
        Column('delta_perc', 'Change %', 100),
        Column('budgeted', 'Budgeted', 100),
    ]
    EXPANDED_NODE_PREF_NAME = 'profitLossExpandedPaths'
    
    def _getModel(self):
        return IncomeStatementModel(view=self, document=self.doc.model)
    
