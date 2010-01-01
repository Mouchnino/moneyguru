# Created By: Virgil Dupras
# Created On: 2008-09-04
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# The code difference between the various account related pie chart is way too small, that's why
# they're all grouped here.

from collections import defaultdict
from datetime import date

from ..model.account import ASSET, LIABILITY, INCOME, EXPENSE
from ..model.amount import convert_amount
from ..model.date import DateRange
from .pie_chart import PieChart

class _AccountPieChart(PieChart):
    def __init__(self, view, document, account_type, title):
        PieChart.__init__(self, view, document)
        self._account_type = account_type
        self._title = title
    
    #--- Protected
    def _get_account_data(self): # Virtual
        raise NotImplementedError()
    
    def _get_data(self): # Override
        account_data = self._get_account_data()
        data = defaultdict(int)
        for account, amount in account_data:
            name = account.name
            if (account.group is not None) and (not account.group.expanded):
                name = account.group.name
            data[name] += amount
        return data
    
    def _accounts(self):
        accounts = set(a for a in self.document.accounts if a.type == self._account_type)
        return accounts - self.document.excluded_accounts
    
    #--- Properties
    @property
    def title(self):
        return self._title
    
    #--- Event Handlers
    def accounts_excluded(self):
        self.compute()
        self.view.refresh()
    
    def group_expanded_state_changed(self):
        self.compute()
        self.view.refresh()
    

class _BalancePieChart(_AccountPieChart):
    #--- Override
    def _get_account_data(self):
        date = self.document.date_range.end
        currency = self.app.default_currency
        def get_value(account):
            balance = account.normal_balance(date=date, currency=currency)
            budget_date_range = DateRange(date.min, self.document.date_range.end)
            budgeted = self.document.budgeted_amount_for_target(account, budget_date_range)
            budgeted = convert_amount(budgeted, currency, date)
            return balance + budgeted
        
        return [(a, get_value(a)) for a in self._accounts()]
    

class AssetsPieChart(_BalancePieChart):
    def __init__(self, view, document):
        _BalancePieChart.__init__(self, view, document, ASSET, 'Assets')
    

class LiabilitiesPieChart(_BalancePieChart):
    def __init__(self, view, document):
        _BalancePieChart.__init__(self, view, document, LIABILITY, 'Liabilities')
    

class _CashFlowPieChart(_AccountPieChart):
    #--- Override
    def _get_account_data(self):
        date_range = self.document.date_range
        currency = self.app.default_currency
        def get_value(account):
            cash_flow = account.normal_cash_flow(date_range, currency=currency)
            budgeted = self.document.budgets.normal_amount_for_account(account, date_range, currency=currency)
            return cash_flow + budgeted
        
        return [(a, get_value(a)) for a in self._accounts()]
    

class IncomePieChart(_CashFlowPieChart):
    def __init__(self, view, document):
        _CashFlowPieChart.__init__(self, view, document, INCOME, 'Income')
    

class ExpensesPieChart(_CashFlowPieChart):
    def __init__(self, view, document):
        _CashFlowPieChart.__init__(self, view, document, EXPENSE, 'Expenses')
    
