# Created By: Virgil Dupras
# Created On: 2008-09-04
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# The code difference between the various account related pie chart is way too small, that's why
# they're all grouped here.

from collections import defaultdict
from datetime import date

from hscommon.trans import tr
from ..model.account import AccountType
from ..model.amount import convert_amount
from ..model.date import DateRange
from .base import SheetViewNotificationsMixin
from .pie_chart import PieChart

class _AccountPieChart(PieChart, SheetViewNotificationsMixin):
    INVALIDATING_MESSAGES = PieChart.INVALIDATING_MESSAGES | {'accounts_excluded',
        'group_expanded_state_changed'}
    
    def __init__(self, parent_view, title):
        PieChart.__init__(self, parent_view)
        self._title = title
    
    #--- Protected
    def _get_account_data(self, accounts): # Virtual
        raise NotImplementedError()
    
    def _get_data_for_account_type(self, account_type): # Override
        accounts = self._accounts(account_type)
        account_data = self._get_account_data(accounts)
        data = defaultdict(int)
        for account, amount in account_data:
            name = account.name
            if (account.group is not None) and (not account.group.expanded):
                name = account.group.name
            data[name] += amount
        return data
    
    def _accounts(self, account_type):
        accounts = {a for a in self.document.accounts if a.type == account_type}
        return accounts - self.document.excluded_accounts
    
    #--- Properties
    @property
    def title(self):
        return self._title
    
    #--- Event Handlers
    def accounts_excluded(self):
        self._revalidate()
    
    def group_expanded_state_changed(self):
        self._revalidate()
    

class BalancePieChart(_AccountPieChart):
    def __init__(self, networth_view):
        _AccountPieChart.__init__(self, networth_view, tr('Assets & Liabilities'))
    
    #--- Override
    def _get_account_data(self, accounts):
        date = self.document.date_range.end
        currency = self.document.default_currency
        def get_value(account):
            balance = account.entries.normal_balance(date=date, currency=currency)
            budget_date_range = DateRange(date.min, self.document.date_range.end)
            budgeted = self.document.budgeted_amount_for_target(account, budget_date_range)
            budgeted = convert_amount(budgeted, currency, date)
            return balance + budgeted
        
        return [(a, get_value(a)) for a in accounts]
    
    def _get_data(self):
        return (self._get_data_for_account_type(AccountType.Asset),
            self._get_data_for_account_type(AccountType.Liability))

class CashFlowPieChart(_AccountPieChart):
    def __init__(self, profit_view):
        _AccountPieChart.__init__(self, profit_view, tr('Income & Expenses'))
    
    #--- Override
    def _get_account_data(self, accounts):
        date_range = self.document.date_range
        currency = self.document.default_currency
        def get_value(account):
            cash_flow = account.entries.normal_cash_flow(date_range, currency=currency)
            budgeted = self.document.budgets.normal_amount_for_account(account, date_range, currency=currency)
            return cash_flow + budgeted
        
        return [(a, get_value(a)) for a in accounts]
    
    def _get_data(self):
        return (self._get_data_for_account_type(AccountType.Income),
            self._get_data_for_account_type(AccountType.Expense))
    
