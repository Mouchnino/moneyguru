# Unit Name: moneyguru.model.oven
# Created By: Virgil Dupras
# Created On: 2008-09-14
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date
from operator import attrgetter

from .amount import convert_amount
from .transaction import Entry

class Oven(object):
    def __init__(self, accounts, transactions, scheduled):
        self._accounts = accounts
        self._transactions = transactions
        self._scheduled = scheduled
        self._cooked_until = date.min
        self.transactions = [] # cooked
    
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
        spawns = []
        for recurrence in self._scheduled:
            # the first spawn is the same as txn, don't add it
            spawns += recurrence.get_spawns(until_date)
        txns = self._transactions + spawns
        tocook = [t for t in txns if from_date <= t.date <= until_date]
        tocook.sort(key=attrgetter('date'))
        for txn in tocook:
            self._cook_transaction(txn)
            self.transactions.append(txn)
        self._cooked_until = until_date
    
