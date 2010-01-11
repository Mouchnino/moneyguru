# Created By: Virgil Dupras
# Created On: 2007-11-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

import bisect
from functools import partial
from itertools import takewhile

from hsutil.misc import flatten

from .amount import convert_amount
from .sort import sort_string
from ..exception import DuplicateAccountNameError

class AccountType(object):
    Asset = 'asset'
    Liability = 'liability'
    Income = 'income'
    Expense = 'expense'
    InOrder = [Asset, Liability, Income, Expense]
    All = set(InOrder)

# Placeholder when an argument is not given
NOT_GIVEN = object()

def sort_accounts(accounts):
    """Sort accounts according first to their type, then to their name.
    """
    accounts.sort(key=lambda a: (AccountType.InOrder.index(a.type), sort_string(a.name)))

class Account(object):
    def __init__(self, name, currency, type):
        self.name = name
        self.currency = currency
        self.entries = []
        self.type = type
        self.reference = None
        self.group = None
        self.account_number = ''
        self._date2entries = {}
        self._sorted_entry_dates = []
        # the key for this dict is (date_range, currency)
        self._daterange2cashflow = {}
        
    def __repr__(self):
        return '<Account %r>' % self.name
    
    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __cmp__(self, other):
        # This will be called only for inequalities because __eq__() and
        # __ne__() are defined for this class too.
        return cmp(sort_string(self.name), sort_string(other.name))
    
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
    
    def _normalize_amount(self, amount):
        return -amount if self.is_credit_account() else amount
    
    #--- Public
    def add_entry(self, entry):
        # add_entry() calls must *always* be made in order
        self.entries.append(entry)
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
        currency = currency or self.currency
        cache_key = (date_range, currency)
        if cache_key not in self._daterange2cashflow:
            cash_flow = self._cash_flow(date_range, currency)
            self._daterange2cashflow[cache_key] = cash_flow
        return self._daterange2cashflow[cache_key]
    
    def clear(self, from_date):
        if from_date is None:
            self.entries = []
            self._date2entries = {}
            self._daterange2cashflow = {}
            self._sorted_entry_dates = []
        else:
            self.entries = list(takewhile(lambda e: e.date < from_date, self.entries))
            index = bisect.bisect_left(self._sorted_entry_dates, from_date)
            for date in self._sorted_entry_dates[index:]:
                del self._date2entries[date]
            for date_range, currency in self._daterange2cashflow.keys():
                if date_range.end >= from_date:
                    del self._daterange2cashflow[(date_range, currency)]
            del self._sorted_entry_dates[index:]
    
    def is_balance_sheet_account(self):
        return self.type in (AccountType.Asset, AccountType.Liability)
    
    def is_credit_account(self):
        return self.type in (AccountType.Liability, AccountType.Income)
    
    def is_debit_account(self):
        return self.type in (AccountType.Asset, AccountType.Expense)
    
    def is_income_statement_account(self):
        return self.type in (AccountType.Income, AccountType.Expense)
    
    def last_entry(self, date=None):
        if self.entries:
            if date is None:
                return self.entries[-1]
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
        return self._normalize_amount(balance)
    
    def normal_balance_of_reconciled(self, date=None, currency=None):
        balance = self.balance_of_reconciled(date=date, currency=currency)
        return self._normalize_amount(balance)
    
    def normal_cash_flow(self, date_range, currency=None):
        cash_flow = self.cash_flow(date_range, currency)
        return self._normalize_amount(cash_flow)
    
    #--- Properties
    @property
    def combined_display(self):
        if self.account_number:
            return "{0} - {1}".format(self.account_number, self.name)
        else:
            return self.name
    

class Group(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.expanded = False
    
    def __repr__(self):
        return '<Group %s>' % self.name
    
    def __eq__(self, other):
        return self is other
    
    def __ne__(self, other):
        return self is not other
    
    def __cmp__(self, other):
        # This will be called only for inequalities because __eq__() and
        # __ne__() are defined for this class too.
        return cmp(sort_string(self.name), sort_string(other.name))
    

def new_name(base_name, search_func):
    name = base_name
    index = 0
    while search_func(name) is not None:
        index += 1
        name = '%s %d' % (base_name, index)
    return name

class AccountList(list):
    def __init__(self, default_currency):
        list.__init__(self)
        self.default_currency = default_currency
        self.auto_created = set()
    
    def add(self, account):
        if self.find_reference(account.reference) is None:
            list.append(self, account)
    
    def clear(self):
        del self[:]
    
    def filter(self, group=NOT_GIVEN, type=NOT_GIVEN):
        result = self
        if group is not NOT_GIVEN:
            result = (a for a in result if a.group == group)
        if type is not NOT_GIVEN:
            result = (a for a in result if a.type == type)
        return list(result)
    
    def find(self, name, auto_create_type=None):
        """Returns the first account matching with 'name' (case insensitive)
        
        If 'auto_create_type' is not None and no account is found, create an account of type
        'auto_create_type' and return it.
        """
        lowered = name.lower()
        for account in self:
            if account.name.lower() == lowered:
                return account
            elif account.account_number and lowered.startswith(account.account_number):
                return account
        if auto_create_type:
            account = Account(name, self.default_currency, type=auto_create_type)
            self.add(account)
            self.auto_created.add(account)
            return account
    
    def find_reference(self, reference):
        if reference is None:
            return None
        for account in self:
            if account.reference == reference:
                return account
    
    def new_name(self, base_name):
        return new_name(base_name, self.find)
    
    def remove(self, account):
        list.remove(self, account)
        self.auto_created.discard(account)
    
    def set_account_name(self, account, new_name):
        if not new_name:
            return
        other = self.find(new_name)
        if (other is not None) and (other is not account):
            raise DuplicateAccountNameError()
        account.name = new_name
    

class GroupList(list):
    def clear(self):
        del self[:]
    
    def filter(self, type=NOT_GIVEN):
        result = self
        if type is not NOT_GIVEN:
            result = (g for g in result if g.type == type)
        return list(result)
    
    def find(self, name, base_type):
        lowered = name.lower()
        for item in self:
            if item.name.lower() == lowered and item.type == base_type:
                return item
    
    def new_name(self, base_name, base_type):
        return new_name(base_name, partial(self.find, base_type=base_type))
    
    def set_group_name(self, group, newname):
        other = self.find(newname, group.type)
        if (other is not None) and (other is not group):
            raise DuplicateAccountNameError()
        group.name = newname
    
