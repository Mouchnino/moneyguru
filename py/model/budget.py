# coding: utf-8 
# Created By: Virgil Dupras
# Created On: 2009-06-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# ABOUT BUDGETS
# Budgets work very similarly to recurrences, except that a twist must be applied to them so they
# can work properly. The twist is about the spawn's "recurrence" date and the effective date. The
# recurrence date must be at the beginning of the period, but the effective date must be at the end
# of it. The reason for it is that since recurrence are only cooked until a certain date (usually
# the current date range's end), but that the budget is affects the date range *prior* to it, the
# last budget of the date range will never be represented.

from datetime import date

from hsutil.misc import extract, first

from ..const import REPEAT_MONTHLY
from .amount import prorate_amount
from .date import DateRange, inc_month, ONE_DAY
from .recurrence import Recurrence, Spawn
from .transaction import Transaction, Split

class BudgetSpawn(Spawn):
    is_budget = True
    
    def budget_for_account(self, account, date_range, currency):
        amount = self.amount_for_account(account, currency)
        if not amount:
            return 0
        my_start_date = max(self.recurrence_date, date.today() + ONE_DAY)
        my_end_date = self.date
        my_date_range = DateRange(my_start_date, my_end_date)
        return prorate_amount(amount, my_date_range, date_range)
    

class Budget(Recurrence):
    def __init__(self, account, target, amount, ref_date):
        if account.is_credit_account():
            amount = -amount
        self._account = account
        self._target = target
        self._amount = amount
        ref = Transaction(ref_date)
        Recurrence.__init__(self, ref, REPEAT_MONTHLY, 1, include_first=True)
        self._update_ref_splits()
    
    def __repr__(self):
        return '<Budget %r %r %r>' % (self._account, self._target, self._amount)
    
    def _update_ref_splits(self):
        ref = self.ref
        ref.set_splits([Split(ref, self._account, self._amount), Split(ref, self._target, -self._amount)])
    
    #--- Override
    def _create_spawn(self, ref, recurrence_date):
        # `recurrence_date` is the date at which the budget *starts*.
        end_date = inc_month(recurrence_date, 1) - ONE_DAY
        return BudgetSpawn(self, ref, recurrence_date=recurrence_date, date=end_date)
    
    def get_spawns(self, end, transactions):
        # transactions will affect the amounts of the budget spawns
        spawns = Recurrence.get_spawns(self, end)
        account = self._account
        budget_amount = self._amount
        relevant_transactions = [t for t in transactions if account in t.affected_accounts()]
        for spawn in spawns:
            affects_spawn = lambda t: spawn.recurrence_date <= t.date <= spawn.date
            wheat, shaft = extract(affects_spawn, relevant_transactions)
            relevant_transactions = shaft
            txns_amount = sum(t.amount_for_account(account, budget_amount.currency) for t in wheat)
            spawn_split = first(s for s in spawn.splits if s.account is account)
            if abs(txns_amount) < abs(budget_amount):
                spawn_split.amount = budget_amount - txns_amount
            else:
                spawn_split.amount = 0
            spawn.balance_two_way(spawn_split)
        return spawns
    
    #--- Properties
    @property
    def account(self):
        return self._account
    
    @property
    def amount(self):
        return self._amount
    
    @amount.setter
    def amount(self, value):
        self._amount = value
        self._update_ref_splits()
    
    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, value):
        self._target = value
        self._update_ref_splits()
    
