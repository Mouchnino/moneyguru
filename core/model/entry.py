# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-07-29
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import bisect
from collections import Sequence
from itertools import takewhile

from hsutil.misc import flatten
from .amount import convert_amount, same_currency

class Entry(object):
    def __init__(self, split, amount, balance, reconciled_balance, balance_with_budget):
        self.split = split
        self.amount = amount
        self.balance = balance
        self.reconciled_balance = reconciled_balance
        self.balance_with_budget = balance_with_budget
    
    def __repr__(self):
        return '<Entry %r %r>' % (self.date, self.description)
    
    def change_amount(self, amount):
        assert len(self.splits) == 1
        self.split.amount = amount
        other_split = self.splits[0]
        is_mct = False
        if not same_currency(amount, other_split.amount):
            is_asset = self.account is not None and self.account.is_balance_sheet_account()
            other_is_asset = other_split.account is not None and other_split.account.is_balance_sheet_account()
            if is_asset and other_is_asset:
                is_mct = True
        if is_mct: # don't touch other side unless we have a logical imbalance
            if self.split.is_on_same_side(other_split):
                other_split.amount *= -1
        else:
            other_split.amount = -amount
    
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
    

class EntryList(Sequence):
    def __init__(self, account):
        self.account = account
        self._entries = []
        self._date2entries = {}
        self._sorted_entry_dates = []
        # the key for this dict is (date_range, currency)
        self._daterange2cashflow = {}
    
    def __getitem__(self, key):
        return self._entries.__getitem__(key)
    
    def __len__(self):
        return len(self._entries)
    
    #--- Private
    def _balance(self, balance_attr, date=None, currency=None):
        entry = self.last_entry(date) if date else self.last_entry()
        if entry:
            balance = getattr(entry, balance_attr)
            if currency:
                return convert_amount(balance, currency, date)
            else:
                return balance
        else:
            return 0
    
    def _cash_flow(self, date_range, currency):
        cache = self._date2entries
        entries = flatten(cache[date] for date in date_range if date in cache)
        entries = (e for e in entries if not getattr(e.transaction, 'is_budget', False))
        amounts = (convert_amount(e.amount, currency, e.date) for e in entries)
        return sum(amounts)
    
    #--- Public
    def add_entry(self, entry):
        # add_entry() calls must *always* be made in order
        self._entries.append(entry)
        date = entry.date
        try:
            self._date2entries[date].append(entry)
        except KeyError:
            self._date2entries[date] = [entry]
        if not self._sorted_entry_dates or self._sorted_entry_dates[-1] < date:
            self._sorted_entry_dates.append(date)
    
    def balance(self, date=None, currency=None):
        return self._balance('balance', date, currency=currency)
    
    def balance_of_reconciled(self, date=None, currency=None):
        return self._balance('reconciled_balance', date, currency=currency)
    
    def balance_with_budget(self, date=None, currency=None):
        return self._balance('balance_with_budget', date, currency=currency)
    
    def cash_flow(self, date_range, currency=None):
        currency = currency or self.account.currency
        cache_key = (date_range, currency)
        if cache_key not in self._daterange2cashflow:
            cash_flow = self._cash_flow(date_range, currency)
            self._daterange2cashflow[cache_key] = cash_flow
        return self._daterange2cashflow[cache_key]
    
    def clear(self, from_date):
        if from_date is None:
            self._entries = []
            self._date2entries = {}
            self._daterange2cashflow = {}
            self._sorted_entry_dates = []
        else:
            self._entries = list(takewhile(lambda e: e.date < from_date, self._entries))
            index = bisect.bisect_left(self._sorted_entry_dates, from_date)
            for date in self._sorted_entry_dates[index:]:
                del self._date2entries[date]
            for date_range, currency in self._daterange2cashflow.keys():
                if date_range.end >= from_date:
                    del self._daterange2cashflow[(date_range, currency)]
            del self._sorted_entry_dates[index:]
    
    def last_entry(self, date=None):
        if self._entries:
            if date is None:
                return self._entries[-1]
            else:
                if date not in self._date2entries: # find the nearest smaller date
                    index = bisect.bisect_right(self._sorted_entry_dates, date) - 1
                    if index < 0:
                        return None
                    date = self._sorted_entry_dates[index]
                return self._date2entries[date][-1]
        return None
    
    def normal_balance(self, date=None, currency=None):
        balance = self.balance(date=date, currency=currency)
        return self.account.normalize_amount(balance)
    
    def normal_balance_of_reconciled(self, date=None, currency=None):
        balance = self.balance_of_reconciled(date=date, currency=currency)
        return self.account.normalize_amount(balance)
    
    def normal_cash_flow(self, date_range, currency=None):
        cash_flow = self.cash_flow(date_range, currency)
        return self.account.normalize_amount(cash_flow)
    
