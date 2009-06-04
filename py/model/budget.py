# coding: utf-8 
# Unit Name: moneyguru.model.budget
# Created By: Virgil Dupras
# Created On: 2009-06-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# ABOUT BUDGETS
# Budgets work very similarly to recurrences, except that a twist must be applied to them so they
# can work properly. The twist is about the spawn's "recurrence" date and the effective date. The
# recurrence date must be at the beginning of the period, but the effective date must be at the end
# of it. The reason for it is that since recurrence are only cooked until a certain date (usually
# the current date range's end), but that the budget is affects the date range *prior* to it, the
# last budget of the date range will never be represented.

from hsutil.misc import extract, first

from ..const import REPEAT_MONTHLY
from .date import inc_month
from .recurrence import Recurrence, Spawn
from .transaction import Transaction

class BudgetSpawn(Spawn):
    is_budget = True

class Budget(Recurrence):
    def __init__(self, account, ref_date):
        ref = Transaction(ref_date, account=account, amount=account.budget)
        Recurrence.__init__(self, ref, REPEAT_MONTHLY, 1, include_first=True)
        self._account = account
    
    #--- Override
    def _create_spawn(self, ref, date):
        account = self._account
        budget = account.budget
        spawn = BudgetSpawn(self, ref, date)
        prev_date = inc_month(spawn.date, -1)
        affects_spawn = lambda t: prev_date <= t.date < spawn.date
        wheat, shaft = extract(affects_spawn, self._relevant_transactions)
        self._relevant_transactions = shaft
        amount = sum(t.amount_for_account(account, budget.currency) for t in wheat)
        spawn_split = first(s for s in spawn.splits if s.account is account)
        spawn_split.amount = max(spawn_split.amount - amount, 0)
        spawn.balance_two_way(spawn_split)
        return spawn
    
    def get_spawns(self, end, transactions):
        # transactions will affect the amounts of the budget spawns
        self._relevant_transactions = [t for t in transactions if self._account in t.affected_accounts()]
        return Recurrence.get_spawns(self, end)
    
