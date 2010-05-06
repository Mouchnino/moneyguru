# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-05-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.date import DateRange
from .balance_graph import BalanceGraph

class AccountBalanceGraph(BalanceGraph):
    def __init__(self, view, account_view):
        BalanceGraph.__init__(self, view, account_view.mainwindow)
        self.account_view = account_view
        self._account = None
    
    def _balance_for_date(self, date):
        if self._account is None:
            return 0
        entry = self._account.last_entry(date=date)
        return entry.normal_balance() if entry else 0
    
    def _budget_for_date(self, date):
        date_range = DateRange(date.min, date)
        return self.document.budgeted_amount_for_target(self._account, date_range)
    
    def compute_data(self):
        self._account = self.document.shown_account
        BalanceGraph.compute_data(self)
    
    #--- Event Handlers
    account_must_be_shown = BalanceGraph._data_changed
    
    #--- Properties
    @property
    def title(self):
        return self.document.shown_account.name
    
    @property
    def currency(self):
        return self._account.currency