# Unit Name: moneyguru.gui.net_worth_graph
# Created By: Virgil Dupras
# Created On: 2008-08-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from ..model.date import DateRange
from .balance_graph import BalanceGraph

class NetWorthGraph(BalanceGraph):
    def _balance_for_date(self, date):
        balances = (a.balance(date=date, currency=self._currency) for a in self._accounts)
        return sum(balances)
    
    def _budget_for_date(self, date):
        date_range = DateRange(date.min, date)
        return self.document.accounts.budgeted_amount_for_target(None, date_range)
    
    def compute_data(self):
        accounts = set(a for a in self.document.accounts if a.is_balance_sheet_account())
        self._accounts = accounts - self.document.excluded_accounts
        self._currency = self.app.default_currency
        BalanceGraph.compute_data(self)
    
    #--- Event Handlers
    def accounts_excluded(self):
        self.compute()
        self.view.refresh()
    
    #--- Properties
    @property
    def title(self):
        return 'Net Worth'
    
    @property
    def currency(self):
        return self.app.default_currency
    
