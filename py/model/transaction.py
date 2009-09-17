# Created By: Eric Mc Sween
# Created On: 2008-03-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import time
from collections import defaultdict
from copy import copy

from hsutil.misc import allsame, first

from ..const import NOEDIT
from .account import ASSET, LIABILITY
from .amount import Amount, convert_amount

class Transaction(object):
    def __init__(self, date, description=None, payee=None, checkno=None, account=None, amount=None):
        self.date = date
        self.description = description or ''
        self.payee = payee or ''
        self.checkno = checkno or ''
        if amount is not None:
            self.splits = [Split(self, account, amount), Split(self, None, -amount)]
        else:
            self.splits = []
        self.position = 0
        self.mtime = 0
    
    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.date, self.description)
    
    @classmethod
    def from_transaction(cls, transaction, link_splits=False):
        # The goal here is to have a deepcopy of self, but *without copying the accounts*. We want
        # the splits to link to the same account instances.
        txn = transaction
        result = cls(txn.date, txn.description, txn.payee, txn.checkno)
        result.position = txn.position
        result.mtime = txn.mtime
        for split in txn.splits:
            newsplit = copy(split)
            newsplit.transaction = result
            if link_splits:
                newsplit.original = split
            result.splits.append(newsplit)
        return result
    
    def amount_for_account(self, account, currency):
        splits = (s for s in self.splits if s.account is account)
        return sum(convert_amount(s.amount, currency, self.date) for s in splits)
    
    def affected_accounts(self):
        return set(s.account for s in self.splits if s.account is not None)
    
    def balance_two_way(self, strong_split):
        """Balance a 2-split transaction in a way that 'strong_split' impose itself on the other part"""
        assert len(self.splits) == 2
        weak_split = self.splits[0]
        if weak_split is strong_split:
            weak_split = self.splits[1]
        if strong_split.account and weak_split.account and strong_split.amount and weak_split.amount:
            weak_type = weak_split.account.type
            strong_type = strong_split.account.type
            asset_liability = weak_type in (ASSET, LIABILITY) and strong_type in (ASSET, LIABILITY)
            weak_native = weak_split.amount.currency == weak_split.account.currency
            strong_native = strong_split.amount.currency == strong_split.account.currency
            different_currency = weak_split.amount.currency != strong_split.amount.currency
            if asset_liability and weak_native and strong_native and different_currency:
                # MCT
                if (weak_split.amount > 0) == (strong_split.amount > 0):
                    # logical imbalance, switch the weak split
                    weak_split.amount = -weak_split.amount
                return
        weak_split.amount = -strong_split.amount
    
    def balance(self, strong_split=None):
        """Balance the transaction
        
        strong_split: the split that initiated the imbalance. Will not be modified.
        """
        currency2balance = defaultdict(int)
        splits_with_amount = (s for s in self.splits if s.amount != 0)
        for split in splits_with_amount:
            currency2balance[split.amount.currency] += split.amount
        imbalanced = filter(None, currency2balance.values()) # filters out zeros (balances currencies)
        if not imbalanced:
            return
        if not allsame(amount > 0 for amount in imbalanced):
            return # not all on the same side
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
        if any(x is not NOEDIT for x in [from_, to, amount]):
            fsplits, tsplits = self.splitted_splits()
            fsplit = fsplits[0] if len(fsplits) == 1 else None
            tsplit = tsplits[0] if len(tsplits) == 1 else None
            if from_ is not NOEDIT and fsplit is not None and from_ is not fsplit.account:
                fsplit.account = from_
            if to is not NOEDIT and tsplit is not None and to != tsplit.account_name:
                tsplit.account = to
            if amount is not NOEDIT and fsplit is not None and tsplit is not None and amount != tsplit.amount:
                fsplit.amount = -amount
                tsplit.amount = amount
        if currency is not NOEDIT:
            tochange = (s for s in self.splits if s.amount and s.amount.currency != currency)
            for split in tochange:
                split.amount = Amount(split.amount.value, currency)
        self.mtime = time.time()
    
    def reassign_account(self, account, reassign_to=None):
        for split in self.splits:
            if split.account is account:
                split.account = reassign_to
    
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
    
    def replicate(self, link_splits=False):
        return Transaction.from_transaction(self, link_splits=link_splits)
    
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
    def __init__(self, transaction, account, amount, memo='', reconciled=False):
        self.transaction = transaction
        self.account = account
        self.memo = memo
        self.amount = amount
        self.reconciled = reconciled
        self.reconciliation_pending = False
        self.reference = None

    def __repr__(self):
        return '<Split %r %s>' % (self.account.name if self.account else None, self.amount)
    
    @property
    def account_name(self):
        return self.account.name if self.account is not None else ''
    

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
    def reconciliation_pending(self):
        return self.split.reconciliation_pending
    
    @property
    def reference(self):
        return self.split.reference
    
