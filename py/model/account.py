# Unit Name: moneyguru.account
# Created By: Virgil Dupras
# Created On: 2007-11-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from __future__ import division

import bisect
import re
import unicodedata
from datetime import date
from functools import partial
from itertools import takewhile

from hsutil.misc import flatten

from .amount import convert_amount
from .date import MonthRange
from ..exception import DuplicateAccountNameError

# Account types
ASSET = 'asset'
LIABILITY = 'liability'
INCOME = 'income'
EXPENSE = 'expense'

# Placeholder when an argument is not given
NOT_GIVEN = object()

# The range of diacritics in Unicode
diacritics = re.compile(u'[\u0300-\u036f\u1dc0-\u1dff]')

def sort_key(s):
    """Returns a normalized version of 's' to be used for sorting."""
    return diacritics.sub('', unicodedata.normalize('NFD', unicode(s)).lower())

class Account(object):
    def __init__(self, name, currency, type):
        self.name = name
        self.currency = currency
        self.entries = []
        self.type = type
        self.reference = None
        self.group = None
        self.budget = 0
        self.budget_target = None
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
        return cmp(sort_key(self.name), sort_key(other.name))
    
    #--- Private
    def _cash_flow(self, date_range, currency):
        cache = self._date2entries
        entries = flatten(cache[date] for date in date_range if date in cache)
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
    
    def balance(self, date=None, reconciled=False, currency=None):
        entry = self.last_entry(date) if date else self.last_entry()
        if entry:
            balance = entry.reconciled_balance if reconciled else entry.balance
            if currency:
                return convert_amount(balance, currency, date)
            else:
                return balance
        else:
            return 0
    
    def budgeted_amount(self, date_range, currency=None):
        if not (self.budget and date_range.future):
            return 0
        currency = currency or self.currency
        result = 0
        budget = -self.budget if self.is_credit_account() else self.budget
        budget = convert_amount(budget, currency, date.today())
        start_date = max(date_range.future.start, date_range.start)
        month_range = MonthRange(start_date)
        current_range = month_range & date_range
        while current_range:
            prior_cash_flow = self._cash_flow(month_range, currency)
            if self._normalize_amount(budget) > self._normalize_amount(prior_cash_flow):
                budget_diff = budget - prior_cash_flow
                time_left = month_range.future
                our_time = time_left & date_range
                budget_proportionned = budget_diff * (our_time.days / time_left.days)
                result += budget_proportionned
            month_range = month_range.next()
            current_range = month_range & date_range
        return result
    
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
        return self.type in (ASSET, LIABILITY)
    
    def is_credit_account(self):
        return self.type in (LIABILITY, INCOME)
    
    def is_debit_account(self):
        return self.type in (ASSET, EXPENSE)
    
    def is_income_statement_account(self):
        return self.type in (INCOME, EXPENSE)
    
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
    
    def normal_balance(self, date=None, reconciled=False, currency=None):
        balance = self.balance(date=date, reconciled=reconciled, currency=currency)
        return self._normalize_amount(balance)
    
    def normal_budgeted_amount(self, date_range, currency=None):
        budgeted_amount = self.budgeted_amount(date_range, currency)
        return self._normalize_amount(budgeted_amount)
    
    def normal_cash_flow(self, date_range, currency=None):
        cash_flow = self.cash_flow(date_range, currency)
        return self._normalize_amount(cash_flow)
    

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
        return cmp(sort_key(self.name), sort_key(other.name))
    

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
        self.excluded = set()
    
    def add(self, account):
        if self.find_reference(account.reference) is None:
            list.append(self, account)
    
    def budgeted_amount_for_target(self, target, date_range):
        """ Returns the sum of all the budgeted amounts targeting 'target'. The currency os the 
            result is target's currency. Note that for budgets targeting no account, the target
            is the first asset by default. The result is also normalized (reverted is target is a
            liability). If target is None, all accounts are used
        """
        accounts = set(a for a in self if a.is_income_statement_account())
        accounts -= self.excluded
        if target is None:
            targeters = [a for a in accounts if a.budget and a.budget_target not in self.excluded]
            currency = self.default_currency
        else:
            targeters = [a for a in accounts if a.budget_target is target]
            currency = target.currency
        if not targeters:
            return 0
        budgeted_amount = sum(a.budgeted_amount(date_range, currency=currency) for a in targeters)
        if target is not None:
            budgeted_amount = target._normalize_amount(budgeted_amount)
        return budgeted_amount
    
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
        for item in self:
            if item.name.lower() == lowered:
                return item
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
    
