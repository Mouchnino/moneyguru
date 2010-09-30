# Created By: Virgil Dupras
# Created On: 2007-11-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license



from functools import partial

from .entry import EntryList
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
        self.type = type
        self.reference = None
        self.group = None
        self.account_number = ''
        self.notes = ''
        # entries are filled by the Oven
        self.entries = EntryList(self)
        
    def __repr__(self):
        return '<Account %r>' % self.name
    
    def __lt__(self, other):
        return sort_string(self.name) < sort_string(other.name)
    
    #--- Public
    def normalize_amount(self, amount):
        return -amount if self.is_credit_account() else amount
    
    def is_balance_sheet_account(self):
        return self.type in (AccountType.Asset, AccountType.Liability)
    
    def is_credit_account(self):
        return self.type in (AccountType.Liability, AccountType.Income)
    
    def is_debit_account(self):
        return self.type in (AccountType.Asset, AccountType.Expense)
    
    def is_income_statement_account(self):
        return self.type in (AccountType.Income, AccountType.Expense)
    
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
    
    def __lt__(self, other):
        return sort_string(self.name) < sort_string(other.name)
    

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
    
