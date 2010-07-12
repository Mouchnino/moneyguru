# Created By: Virgil Dupras
# Created On: 2008-07-03
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_, assert_raises

from hscommon.currency import Currency, CAD

from ..base import TestCase
from ...exception import OperationAborted
from ...model.account import AccountType

class SomeAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('foobar', CAD, account_type=AccountType.Expense,
            account_number='4242')
        self.mainwindow.select_income_statement()
        self.clear_gui_calls()
    
    def test_change_currency_index(self):
        # Changing currency_index correctly updates the currency.
        self.apanel.currency_index = 0
        eq_(self.apanel.currency, Currency.all[0])
        self.apanel.currency_index = 42
        eq_(self.apanel.currency, Currency.all[42])
        self.apanel.currency_index = 9999 # doesn't do anything
        eq_(self.apanel.currency, Currency.all[42])
        eq_(self.apanel.currency_index, 42)
    
    def test_change_type_index(self):
        # Changing type_index correctly updates the type.
        self.apanel.type_index = 0
        eq_(self.apanel.type, AccountType.Asset)
        self.apanel.type_index = 1
        eq_(self.apanel.type, AccountType.Liability)
        self.apanel.type_index = 2
        eq_(self.apanel.type, AccountType.Income)
        self.apanel.type_index = 4 # doesn't do anything
        eq_(self.apanel.type, AccountType.Income)
        eq_(self.apanel.type_index, 2)
    
    def test_fields(self):
        # The base field values.
        self.mainwindow.edit_item()
        eq_(self.apanel.name, 'foobar')
        eq_(self.apanel.type, AccountType.Expense)
        eq_(self.apanel.currency, CAD)
        eq_(self.apanel.type_index, 3) # Expense type is last in the list
        eq_(self.apanel.currency_index, Currency.all.index(CAD))
        eq_(self.apanel.account_number, '4242')
    
    def test_fields_before_load(self):
        # ensure no crash occurs
        self.apanel.type_index
    
    def test_load_stops_edition(self):
        # edition must be stop on apanel load or else an account type change can result in a crash
        self.mainwindow.edit_item()
        self.check_gui_calls(self.istatement_gui, ['stop_editing'])
    
    def test_save(self):
        # save() calls document.change_account with the correct arguments and triggers a refresh on
        # all GUI components.
        self.mainwindow.edit_item()
        self.apanel.type_index = 2
        self.apanel.currency_index = 42
        self.apanel.name = 'foobaz'
        self.apanel.account_number = '4241'
        self.apanel.save()
        # To test the currency, we have to load again
        self.istatement.selected = self.istatement.income[0]
        self.mainwindow.edit_item()
        eq_(self.apanel.currency, Currency.all[42])
        eq_(self.apanel.type, AccountType.Income)
        eq_(self.apanel.name, 'foobaz')
        eq_(self.apanel.account_number, '4241')
    

class TwoAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('foobar')
        self.add_account('foobaz')
        self.clear_gui_calls()
    
    def test_duplicate_name(self):
        # setting a duplicate account name makes the dialog show a warning label
        self.mainwindow.edit_item()
        self.apanel.name = 'foobar'
        self.apanel.save() # the exception doesn't propagate
    
