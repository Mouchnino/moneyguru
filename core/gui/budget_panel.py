# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-08-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from datetime import date

from ..exception import OperationAborted
from ..model.account import sort_accounts
from ..model.budget import Budget
from .base import GUIPanel
from .schedule_panel import PanelWithScheduleMixIn, REPEAT_OPTIONS_ORDER

class BudgetPanel(GUIPanel, PanelWithScheduleMixIn):
    #--- Override
    def _load(self):
        self._load_budget(self.document.selected_budget)
    
    def _new(self):
        self._load_budget(Budget(None, None, 0, date.today()))
    
    def _save(self):
        self.budget.repeat_type = REPEAT_OPTIONS_ORDER[self.repeat_type_index]
        self.budget.account = self._accounts[self.account_index]
        self.budget.target = self._targets[self.target_index]
        self.document.change_budget(self.original, self.budget)
    
    #--- Private
    def _load_budget(self, budget):
        if budget is None:
            raise OperationAborted
        self.original = budget
        self.budget = budget.replicate()
        self.schedule = self.budget # for PanelWithScheduleMixIn
        self._repeat_type_index = REPEAT_OPTIONS_ORDER.index(budget.repeat_type)
        self._accounts = [a for a in self.document.accounts if a.is_income_statement_account()]
        if not self._accounts:
            msg = "Income/Expense accounts must be created before budgets can be set."
            raise OperationAborted(msg)
        sort_accounts(self._accounts)
        self._targets = [a for a in self.document.accounts if a.is_balance_sheet_account()]
        sort_accounts(self._targets)
        self._targets.insert(0, None)
        self.account_options = [a.name for a in self._accounts]
        self.target_options = [(a.name if a is not None else 'None') for a in self._targets]
        self.account_index = self._accounts.index(budget.account) if budget.account is not None else 0
        self.target_index = self._targets.index(budget.target)
        self.view.refresh_repeat_options()
        self.view.refresh_repeat_every()
    
    #--- Properties
    @property
    def amount(self):
        return self.app.format_amount(self.budget.amount)
    
    @amount.setter
    def amount(self, value):
        try:
            self.budget.amount = self.app.parse_amount(value)
        except ValueError:
            pass
    
