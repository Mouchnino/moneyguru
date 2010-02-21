# Created By: Eric Mc Sween
# Created On: 2008-03-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import time
from collections import defaultdict
from copy import copy

from hsutil.misc import allsame, first, nonone

from ..const import NOEDIT
from .account import AccountType
from .amount import Amount, convert_amount, same_currency

class Transaction(object):
    def __init__(self, date, description=None, payee=None, checkno=None, account=None, amount=None):
        self.date = date
        self.description = nonone(description, '')
        self.payee = nonone(payee, '')
        self.checkno = nonone(checkno, '')
        self.amount = nonone(amount, 0)
        if amount is not None:
            self.splits = [Split(self, account, amount), Split(self, None, -amount)]
        else:
            self.splits = []
        self.position = 0
        self.mtime = 0
    
    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.date, self.description)
    
    @classmethod
    def from_transaction(cls, transaction):
        # The goal here is to have a deepcopy of self, but *without copying the accounts*. We want
        # the splits to link to the same account instances.
        txn = transaction
        result = cls(txn.date, txn.description, txn.payee, txn.checkno)
        result.position = txn.position
        result.mtime = txn.mtime
        result.amount = txn.amount
        for split in txn.splits:
            newsplit = copy(split)
            newsplit.transaction = result
            result.splits.append(newsplit)
        return result
    
    def amount_for_account(self, account, currency):
        splits = (s for s in self.splits if s.account is account)
        return sum(convert_amount(s.amount, currency, self.date) for s in splits)
    
    def affected_accounts(self):
        return set(s.account for s in self.splits if s.account is not None)
    
    def balance(self, strong_split=None):
        # For the special case where there is 2 splits on the same "side" and a strong split, we
        # reverse the weak split
        if len(self.splits) == 2 and strong_split is not None:
            weak_split = self.splits[0] if self.splits[0] is not strong_split else self.splits[1]
            if (weak_split.amount > 0) == (strong_split.amount > 0): # on the same side
                weak_split.amount *= -1
        splits_with_amount = [s for s in self.splits if s.amount]
        if splits_with_amount and not allsame(s.amount.currency for s in splits_with_amount):
            self.balance_currencies(strong_split)
            return
        # When the transaction amount is 0, the existing splits then determine what this amount is
        # going to be.
        if not self.amount:
            debits = sum(s.debit for s in self.splits)
            credits = sum(s.credit for s in self.splits)
            self.amount = max(debits, credits)
        debits = sum(s.debit for s in self.splits)
        credits = sum(s.credit for s in self.splits)
        main_debit, main_credit = self.main_splits()
        # when a main split is edited, the amount is adjusted
        if strong_split is main_debit:
            self.amount = debits
        elif strong_split is main_credit:
            self.amount = credits
        if debits == credits == self.amount:
            return
        if debits != self.amount:
            diff = self.amount - debits
            if main_debit is None or main_debit is strong_split:
                self.splits.append(Split(self, None, diff))
            else:
                main_debit.amount += diff
        if credits != self.amount:
            diff = self.amount - credits
            if main_credit is None or main_credit is strong_split:
                self.splits.append(Split(self, None, -diff))
            else:
                main_credit.amount -= diff
    
    def balance_currencies(self, strong_split=None):
        splits_with_amount = [s for s in self.splits if s.amount != 0]
        if not splits_with_amount:
            return
        currency2balance = defaultdict(int)
        for split in splits_with_amount:
            currency2balance[split.amount.currency] += split.amount
        imbalanced = filter(None, currency2balance.values()) # filters out zeros (balances currencies)
        # For a logical imbalance to be possible, all imbalanced amounts must be on the same side
        if imbalanced and allsame(amount > 0 for amount in imbalanced):
            unassigned = [s for s in self.splits if s.account is None and s is not strong_split]
            for amount in imbalanced:
                split = first(s for s in unassigned if s.amount == 0 or s.amount.currency == amount.currency)
                if split is not None:
                    if split.amount == amount: # we end up with a null split, remove it
                        self.splits.remove(split)
                    else:
                        split.amount -= amount # adjust
                else:
                    self.splits.append(Split(self, None, -amount))
        # We need an approximation for the amount value. What we do is we take the currency of the
        # first split and use it as a base currency. Then, we sum up all amounts, convert them, and
        # divide the sum by 2.
        currency = splits_with_amount[0].amount.currency
        convert = lambda a: convert_amount(abs(a), currency, self.date)
        amount_sum = sum(convert(s.amount) for s in splits_with_amount)
        self.amount = amount_sum * 0.5
    
    def change(self, date=NOEDIT, description=NOEDIT, payee=NOEDIT, checkno=NOEDIT, from_=NOEDIT, 
               to=NOEDIT, amount=NOEDIT, currency=NOEDIT):
        # from_ and to are Account instances
        if date is not NOEDIT:
            self.date = date
        if description is not NOEDIT:
            self.description = description
        if payee is not NOEDIT:
            self.payee = payee
        if checkno is not NOEDIT:
            self.checkno = checkno
        if from_ is not NOEDIT:
            fsplits, _ = self.splitted_splits()
            if len(fsplits) == 1:
                fsplit = fsplits[0]
                fsplit.account = from_
        if to is not NOEDIT:
            _, tsplits = self.splitted_splits()
            if len(tsplits) == 1:
                tsplits = tsplits[0]
                tsplits.account = to
        if amount is not NOEDIT:
            if not same_currency(amount, self.amount):
                self.change(currency=amount.currency)
            self.amount = amount
            self.balance()
        if currency is not NOEDIT:
            tochange = (s for s in self.splits if s.amount and s.amount.currency != currency)
            for split in tochange:
                split.amount = Amount(split.amount.value, currency)
            self.amount = Amount(self.amount.value, currency)
        self.mtime = time.time()
    
    def main_splits(self):
        main_debit = first(s for s in self.splits if s.amount > 0)
        main_credit = first(s for s in self.splits if s.amount < 0)
        free_splits = (s for s in self.splits if not s.amount)
        if main_debit is None:
            main_debit = first(free_splits)
        if main_credit is None:
            main_credit = first(free_splits)
        return main_debit, main_credit
    
    def matches(self, query):
        """Return whether 'self' is matching query, which is a dict containing various arguments,
        such as 'all', 'amount', 'account'...
        """
        query_all = query.get('all')
        if query_all is not None:
            if query_all in self.description.lower():
                return True
            if query_all in self.payee.lower():
                return True
            if query_all == self.checkno.lower():
                return True
            for split in self.splits:
                if split.account and query_all in split.account.name.lower():
                    return True
                elif query_all in split.memo:
                    return True
        query_amount = query.get('amount')
        if query_amount is not None:
            query_value = query_amount.value if query_amount else 0
            for split in self.splits:
                split_value = split.amount.value if split.amount else 0
                if query_value == abs(split_value):
                    return True
        query_account = query.get('account')
        if query_account is not None:
            for split in self.splits:
                if split.account and split.account.name.lower() in query_account:
                    return True
        query_group = query.get('group')
        if query_group is not None:
            for split in self.splits:
                if split.account and split.account.group and split.account.group.name.lower() in query_group:
                    return True
        return False
    
    def mct_balance(self, new_split_currency):
        # when calling this, the transaction is supposed to be balanced with balance() already
        converted_amounts = (convert_amount(split.amount, new_split_currency, self.date) for split in self.splits)
        converted_total = sum(converted_amounts)
        if converted_total != 0:
            self.splits.append(Split(self, None, -converted_total))
    
    def reassign_account(self, account, reassign_to=None):
        for split in self.splits:
            if split.account is account:
                split.account = reassign_to
    
    def replicate(self):
        return Transaction.from_transaction(self)
    
    def set_splits(self, splits):
        self.splits = []
        for split in splits:
            newsplit = copy(split)
            newsplit.transaction = self
            self.splits.append(newsplit)
    
    def splitted_splits(self):
        """Returns (froms, tos) where 'froms' is the splits that belong to the 'from' column, and
        'tos', the rest.
        """
        splits = self.splits
        null_amounts = [s for s in splits if s.amount == 0]
        froms = [s for s in splits if s.amount < 0]
        tos = [s for s in splits if s.amount > 0]
        if not tos and null_amounts:
            tos.append(null_amounts.pop())
        froms += null_amounts
        return froms, tos
    
    @property
    def has_unassigned_split(self):
        return any(s.account is None for s in self.splits)
    
    @property
    def is_mct(self):
        splits_with_amount = (s for s in self.splits if s.amount != 0)
        try:
            return not allsame(s.amount.currency for s in splits_with_amount)
        except ValueError: # no split with amount
            return False
    
    @property
    def is_null(self):
        return all(not s.amount for s in self.splits)
    

class Split(object):
    def __init__(self, transaction, account, amount):
        self.transaction = transaction
        self.account = account
        self.memo = ''
        self.amount = amount
        self.reconciliation_date = None
        self.reference = None
    
    def __repr__(self):
        return '<Split %r %s>' % (self.account_name, self.amount)
    
    @property
    def account_name(self):
        return self.account.name if self.account is not None else ''
    
    @property
    def credit(self):
        return -self.amount if self.amount < 0 else 0
    
    @property
    def debit(self):
        return self.amount if self.amount > 0 else 0
    
    @property
    def reconciled(self):
        return self.reconciliation_date is not None
    

class Entry(object):
    def __init__(self, split, amount, balance, reconciled_balance, balance_with_budget):
        self.split = split
        self.amount = amount
        self.balance = balance
        self.reconciled_balance = reconciled_balance
        self.balance_with_budget = balance_with_budget
    
    def __repr__(self):
        return '<Entry %r %r>' % (self.date, self.description)
    
    def change(self, date=NOEDIT, description=NOEDIT, payee=NOEDIT, checkno=NOEDIT):
        self.transaction.change(date=date, description=description, payee=payee, checkno=checkno)
    
    def normal_balance(self):
        is_credit = self.account is not None and self.account.is_credit_account()
        return -self.balance if is_credit else self.balance
    
    @property
    def account(self):
        return self.split.account
    
    @property
    def checkno(self):
        return self.transaction.checkno
    
    @property
    def date(self):
        return self.transaction.date
    
    @property
    def description(self):
        return self.transaction.description
    
    @property
    def payee(self):
        return self.transaction.payee
    
    @property
    def mtime(self):
        return self.transaction.mtime
    
    @property
    def splits(self):
        return [x for x in self.split.transaction.splits if x is not self.split]
    
    @property
    def transaction(self):
        return self.split.transaction
    
    @property
    def transfer(self):
        return [split.account for split in self.splits if split.account is not None]
    
    @property
    def reconciled(self):
        return self.split.reconciled
    
    @property
    def reconciliation_date(self):
        return self.split.reconciliation_date
    
    @property
    def reference(self):
        return self.split.reference
    
