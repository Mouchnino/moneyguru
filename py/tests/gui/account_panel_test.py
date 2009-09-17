# Created By: Virgil Dupras
# Created On: 2008-07-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_, assert_raises

from hsutil.currency import Currency, CAD

from ..base import TestCase, CommonSetup
from ...exception import OperationAborted
from ...model.account import ASSET, LIABILITY, INCOME, EXPENSE

class CommonSetup(CommonSetup):
    def setup_accounts_of_all_types(self):
        # liability created first to force a sorting on the panel side
        self.add_account('liability', account_type=LIABILITY)
        self.add_account('asset', account_type=ASSET)
        self.add_account('income', account_type=INCOME)
        self.add_account('expense', account_type=EXPENSE)
        self.mainwindow.select_income_statement()
    

class SomeAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('foobar', CAD, account_type=EXPENSE)
        self.clear_gui_calls()
    
    def test_can_load(self):
        # Make sure that OperationAborted is raised when appropriate
        self.apanel.load() # no OperationAborted
        self.bsheet.selected = self.bsheet.assets
        assert_raises(OperationAborted, self.apanel.load)
    
    def test_change_currency_index(self):
        """Changing currency_index correctly updates the currency"""
        self.apanel.currency_index = 0
        self.assertEqual(self.apanel.currency, Currency.all[0])
        self.apanel.currency_index = 42
        self.assertEqual(self.apanel.currency, Currency.all[42])
        self.apanel.currency_index = 9999 # doesn't do anything
        self.assertEqual(self.apanel.currency, Currency.all[42])
        self.assertEqual(self.apanel.currency_index, 42)
    
    def test_change_type_index(self):
        """Changing type_index correctly updates the type"""
        self.apanel.type_index = 0
        self.assertEqual(self.apanel.type, ASSET)
        self.apanel.type_index = 1
        self.assertEqual(self.apanel.type, LIABILITY)
        self.apanel.type_index = 2
        self.assertEqual(self.apanel.type, INCOME)
        self.apanel.type_index = 4 # doesn't do anything
        self.assertEqual(self.apanel.type, INCOME)
        self.assertEqual(self.apanel.type_index, 2)
    
    def test_fields(self):
        """The base field values"""
        self.apanel.load()
        self.assertEqual(self.apanel.name, 'foobar')
        self.assertEqual(self.apanel.type, EXPENSE)
        self.assertEqual(self.apanel.currency, CAD)
        self.assertEqual(self.apanel.type_index, 3) # Expense type is last in the list
        self.assertEqual(self.apanel.currency_index, Currency.all.index(CAD))
    
    def test_fields_before_load(self):
        # ensure no crash occurs
        self.apanel.type_index
    
    def test_save(self):
        """save() calls document.change_account with the correct arguments and triggers a refresh on all GUI components."""
        self.apanel.load()
        self.apanel.type_index = 2
        self.apanel.currency_index = 42
        self.apanel.name = 'foobaz'
        self.apanel.budget = '42'
        self.apanel.save()
        # To test the currency, we have to load again
        self.apanel.load()
        self.assertEqual(self.apanel.currency, Currency.all[42])
        self.assertEqual(self.apanel.type, INCOME)
        self.assertEqual(self.apanel.name, 'foobaz')
    

class TwoAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('foobar')
        self.add_account('foobaz')
        self.clear_gui_calls()
    
    def test_duplicate_name(self):
        # setting a duplicate account name makes the dialog show a warning label
        self.apanel.load()
        self.apanel.name = 'foobar'
        self.apanel.save() # the exception doesn't propagate
    
