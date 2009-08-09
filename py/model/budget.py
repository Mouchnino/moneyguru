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

class Budget(Recurrence):
    def __init__(self, account, target, amount, ref_date):
        self.account = account
        self.target = target
        self.amount = amount
        self._previous_spawns = []
        ref = Transaction(ref_date)
        Recurrence.__init__(self, ref, REPEAT_MONTHLY, 1, include_first=True)
    
    def __repr__(self):
        return '<Budget %r %r %r>' % (self.account, self.target, self.amount)
    
    #--- Override
    def _create_spawn(self, ref, recurrence_date):
        # `recurrence_date` is the date at which the budget *starts*.
        end_date = inc_month(recurrence_date, 1) - ONE_DAY
        return BudgetSpawn(self, ref, recurrence_date=recurrence_date, date=end_date)
    
    def get_spawns(self, end, transactions):
        # transactions will affect the amounts of the budget spawns
        spawns = Recurrence.get_spawns(self, end)
        account = self.account
        budget_amount = self.amount if account.is_debit_account() else -self.amount
        relevant_transactions = [t for t in transactions if account in t.affected_accounts()]
        for spawn in spawns:
            affects_spawn = lambda t: spawn.recurrence_date <= t.date <= spawn.date
            wheat, shaft = extract(affects_spawn, relevant_transactions)
            relevant_transactions = shaft
            txns_amount = sum(t.amount_for_account(account, budget_amount.currency) for t in wheat)
            if abs(txns_amount) < abs(budget_amount):
                spawn_amount = budget_amount - txns_amount
                spawn.set_splits([Split(spawn, account, spawn_amount), Split(spawn, self.target, -spawn_amount)])
            else:
                spawn.set_splits([])
        self._previous_spawns = spawns
        return spawns
    
    #--- Public
    def amount_for_date_range(self, date_range, currency):
        total_amount = 0
        for spawn in self._previous_spawns:
            amount = spawn.amount_for_account(self.account, currency)
            if not amount:
                continue
            my_start_date = max(spawn.recurrence_date, date.today() + ONE_DAY)
            my_end_date = spawn.date
            my_date_range = DateRange(my_start_date, my_end_date)
            total_amount += prorate_amount(amount, my_date_range, date_range)
        return total_amount
    

class BudgetList(list):
    def amount_for_account(self, account, date_range, currency=None):
        if not date_range.future:
            return 0
        budget = self.budget_for_account(account)
        if budget is None or not budget.amount:
            return 0
        currency = currency or account.currency
        return budget.amount_for_date_range(date_range, currency)
    
    def budget_for_account(self, account):
        return first(b for b in self if b.account is account)
    
    def budgets_for_target(self, target):
        return [b for b in self if b.target is target]
    
    def normal_amount_for_account(self, account, date_range, currency=None):
        budgeted_amount = self.amount_for_account(account, date_range, currency)
        return account._normalize_amount(budgeted_amount)
    
