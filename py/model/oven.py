# Unit Name: moneyguru.model.oven
# Created By: Virgil Dupras
# Created On: 2008-09-14
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date
from itertools import dropwhile
from operator import attrgetter

from hsutil.misc import flatten

from .amount import convert_amount
from .budget import Budget
from .date import inc_month
from .transaction import Entry

class Oven(object):
    """The Oven takes "raw data" from accounts and transactions and "cooks" calculated data out of
    them, such as running balance and scheduled transaction spawns.
    """
    def __init__(self, accounts, transactions, scheduled):
        self._accounts = accounts
        self._transactions = transactions
        self._scheduled = scheduled
        self._cooked_until = date.min
        self.transactions = [] # cooked
        self.budgets = [] # cooked
    
    def _budget_spawns(self, until_date):
        result = []
        TODAY = date.today()
        ref_date = date(TODAY.year, TODAY.month, 1)
        relevant_txns = list(dropwhile(lambda t: t.date < ref_date, self._transactions))
        account_with_budget = (a for a in self._accounts if a.budget)
        for account in account_with_budget:
            budget = Budget(account, ref_date)
            spawns = budget.get_spawns(until_date, relevant_txns)
            spawns = [spawn for spawn in spawns if not spawn.is_null]
            result += spawns
        return result
    
    def _cook_split(self, split):
        account = split.account
        if account is None:
            return
        amount = split.amount
        converted_amount = convert_amount(amount, account.currency, split.transaction.date)
        balance = account.balance() + converted_amount
        reconciled_balance = account.balance(reconciled=True)
        if split.reconciled or split.reconciliation_pending:
            reconciled_balance += split.amount
        account.add_entry(Entry(split, amount, balance, reconciled_balance))
    
    def _cook_transaction(self, txn):
        for split in txn.splits:
            self._cook_split(split)
    
    def continue_cooking(self, until_date):
        if until_date > self._cooked_until:
            self.cook(self._cooked_until, until_date)
    
    def cook(self, from_date=None, until_date=None):
        """Cooks _accounts, _transactions, and _scheduled into transactions.
        
        from_date: when set, saves calculation time by re-using existing cooked transactions
        until_date: because of recurrence, we must always have a date at which we stop cooking.
                    If we don't, we might end up in an infinite loop.
        """
        for account in self._accounts:
            account.clear(from_date)
        if from_date is None:
            self.transactions = []
        else:
            self.transactions = [t for t in self.transactions if t.date < from_date]
        if not (self or self._scheduled):
            return
        if from_date is None:
            from_date = date.min
        self._transactions.sort(key=attrgetter('date', 'position')) # needed in case until_date is None
        if until_date is None:
            until_date = self._transactions[-1].date if self._transactions else from_date
        spawns = flatten(recurrence.get_spawns(until_date) for recurrence in self._scheduled)
        spawns += self._budget_spawns(until_date)
        txns = self._transactions + spawns
        # we don't filter out txns > until_date because they might be budgets affecting current data
        tocook = [t for t in txns if from_date <= t.date]
        tocook.sort(key=attrgetter('date'))
        for txn in tocook:
            self._cook_transaction(txn)
            self.transactions.append(txn)
        self._cooked_until = until_date
    
