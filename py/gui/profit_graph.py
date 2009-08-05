# Created By: Virgil Dupras
# Created On: 2008-08-20
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.misc import flatten

from .bar_graph import BarGraph

class ProfitGraph(BarGraph):
    #--- Override
    def _currency(self):
        return self.app.default_currency
    
    def _get_cash_flow(self, date_range):
        self.document.oven.continue_cooking(date_range.end) # it's possible that the overflow is not cooked
        accounts = set(a for a in self.document.accounts if a.is_income_statement_account())
        accounts = accounts - self.document.excluded_accounts
        cash_flow = -sum(a.cash_flow(date_range, currency=self.app.default_currency) for a in accounts)
        budgeted_amount = self.document.budgeted_amount_for_target(None, date_range)
        return cash_flow - budgeted_amount
    
    def _is_reverted(self):
        return True
    
    #--- Event Handlers
    def accounts_excluded(self):
        self.compute()
        self.view.refresh()
    
    #--- Properties
    @property
    def title(self):
        return 'Profit & Loss'
    
