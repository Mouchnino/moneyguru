# Created By: Virgil Dupras
# Created On: 2010-05-06
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .bar_graph import BarGraph

class AccountFlowGraph(BarGraph):
    INVALIDATING_MESSAGES = BarGraph.INVALIDATING_MESSAGES
    
    def __init__(self, account_view):
        BarGraph.__init__(self, account_view)
        self._account = account_view.account
    
    #--- Override
    def _currency(self):
        return self._account.currency
    
    def _get_cash_flow(self, date_range):
        self.document.oven.continue_cooking(date_range.end) # it's possible that the overflow is not cooked
        account = self._account
        currency = self._currency()
        cash_flow = account.entries.normal_cash_flow(date_range, currency=currency)
        budgeted = self.document.budgets.normal_amount_for_account(account, date_range, currency=currency)
        return cash_flow + budgeted
    
    #--- Properties
    @property
    def title(self):
        return self._account.name
    
