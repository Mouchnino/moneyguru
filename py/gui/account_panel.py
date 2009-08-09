# Created By: Virgil Dupras
# Created On: 2008-07-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.currency import Currency

from ..const import NOEDIT
from ..exception import DuplicateAccountNameError
from ..model.account import ASSET, LIABILITY, INCOME, EXPENSE
from ..model.amount import Amount, parse_amount, format_amount
from .base import DocumentGUIObject

TYPE_ORDER = [ASSET, LIABILITY, INCOME, EXPENSE]

class AccountPanel(DocumentGUIObject):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        self._init_fields()
    
    def _init_fields(self):
        self.type = ASSET
        self._type_index = 0
        self.currency = None
        self._budget = 0
        self.budget_target_index = 0
        self.available_budget_targets = []
    
    def can_load(self):
        account = self.document.selected_account
        return account is not None
    
    def load(self):
        """Loads the selected account's data"""
        self._init_fields()
        account = self.document.selected_account
        assert account is not None
        self.name = account.name
        self.type = account.type
        self.currency = account.currency
        self.type_index = TYPE_ORDER.index(self.type)
        self.currency_index = Currency.all.index(self.currency)
        self._budget = account.budget
        self._budget_targets = [a for a in self.document.accounts if a.is_balance_sheet_account()]
        self._budget_targets.sort(key=lambda a: (TYPE_ORDER.index(a.type), a.name))
        self.available_budget_targets = [a.name for a in self._budget_targets]
        if account.budget_target in self._budget_targets:
            self.budget_target_index = self._budget_targets.index(account.budget_target)
        self.account = account # for the save() assert
    
    def save(self):
        """Save the panel fields's values into the selected account"""
        assert self.account is self.document.selected_account
        try:
            budget_target = self._budget_targets[self.budget_target_index]
        except IndexError:
            budget_target = None
        try:
            self.document.change_account(self.account, name=self.name, type=self.type, 
                currency=self.currency, budget_amount=self._budget, budget_target=budget_target)
        except DuplicateAccountNameError:
            pass
    
    #--- Properties
    @property
    def budget(self):
        return format_amount(self._budget, self.currency)
    
    @budget.setter
    def budget(self, value):
        try:
            self._budget = parse_amount(value, self.currency)
        except ValueError:
            pass
    
    @property
    def budget_enabled(self):
        return self.type in (INCOME, EXPENSE)
    
    @property
    def currency_index(self):
        return self._currency_index
    
    @currency_index.setter
    def currency_index(self, index):
        try:
            self.currency = Currency.all[index]
            if self._budget:
                self._budget = Amount(self._budget.value, self.currency)
        except IndexError:
            pass
        else:
            self._currency_index = index
    
    @property
    def type_index(self):
        return self._type_index
    
    @type_index.setter
    def type_index(self, index):
        try:
            self.type = TYPE_ORDER[index]
        except IndexError:
            pass
        else:
            self._type_index = index
    
