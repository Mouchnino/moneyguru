# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-08-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..model.account import ACCOUNT_SORT_KEY
from .base import ViewChild
from .column import Column
from .table import GUITable, Row

class CashculatorAccountTable(GUITable, ViewChild):
    INVALIDATING_MESSAGES = {'account_added', 'account_changed', 'account_deleted',
        'accounts_excluded'}
    COLUMNS = [
        Column('name'),
        Column('recurring'),
    ]
    
    def __init__(self, view, cc_view):
        ViewChild.__init__(self, view, cc_view)
        GUITable.__init__(self)
        self.nonrecurring_names = set()
    
    #--- Override
    def _fill(self):
        if self.parent_view.has_db():
            categories = self.parent_view.get_categories()
            nonrec = (cat for cat in categories.values() if not cat.is_recurring)
            self.nonrecurring_names = set(cat.name for cat in nonrec)
        accounts = {a for a in self.document.accounts if a.is_income_statement_account()}
        accounts -= self.document.excluded_accounts
        accounts = sorted(accounts, key=ACCOUNT_SORT_KEY)
        for account in accounts:
            self.append(CashculatorAccountTableRow(self, account))
    
    def _revalidate(self):
        self.refresh()
        self.view.refresh()
    
    #--- Public
    def is_recurring(self, name):
        return name not in self.nonrecurring_names
    
    def set_recurring(self, name, value):
        if value:
            self.nonrecurring_names.discard(name)
        else:
            self.nonrecurring_names.add(name)
    

class CashculatorAccountTableRow(Row):
    def __init__(self, table, account):
        Row.__init__(self, table)
        self.account = account
    
    #--- Public
    def load(self):
        pass # nothing to load
    
    def save(self):
        pass # read-only
    
    #--- Properties
    @property
    def name(self):
        return self.account.name
    
    @property
    def recurring(self):
        return self.table.is_recurring(self.account.name)
    
    @recurring.setter
    def recurring(self, value):
        self.table.set_recurring(self.account.name, value)
    
