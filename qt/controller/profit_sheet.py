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
from .account_sheet import AccountSheet

class ProfitSheet(AccountSheet):
    HEADER = ['Account', 'Current', 'Last', 'Budgeted']
    ROWATTRS = ['name', 'cash_flow', 'last_cash_flow', 'budgeted']
    EXPANDED_NODE_PREF_NAME = 'profitLossExpandedPaths'
    
    def _getModel(self):
        return IncomeStatementModel(view=self, document=self.doc.model)