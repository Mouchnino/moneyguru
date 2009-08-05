# Created By: Virgil Dupras
# Created On: 2008-07-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.currency import Currency, CAD

from ..base import TestCase, CommonSetup
from ...model.account import ASSET, LIABILITY, INCOME, EXPENSE

class CommonSetup(CommonSetup):
    def setup_accounts_of_all_types(self):
        # liability created first to force a sorting on the panel side
        self.add_account('liability', account_type=LIABILITY)
        self.add_account('asset', account_type=ASSET)
        self.add_account('income', account_type=INCOME)
        self.add_account('expense', account_type=EXPENSE)
        self.document.select_income_statement()
    

class SomeAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('foobar', CAD, account_type=EXPENSE)
        self.clear_gui_calls()
    
    def test_budget_enabled(self):
        # the budget fields are only enabled if the account is an income/expense
        self.apanel.load()
        self.assertTrue(self.apanel.budget_enabled)
        self.apanel.type_index = 1
        self.assertFalse(self.apanel.budget_enabled)
    
    def test_can_load(self):
        """The panel can only load if the selected node is an non-special account"""
        self.assertTrue(self.apanel.can_load())
        self.bsheet.selected = self.bsheet.assets
        self.assertFalse(self.apanel.can_load())
    
    def test_change_budget(self):
        # changing budget updates it correctly
        self.apanel.load()
        self.apanel.budget = '54,42'
        self.assertEqual(self.apanel.budget, '54.42')
        self.apanel.budget = 'foo'
        self.assertEqual(self.apanel.budget, '54.42')
    
    def test_change_then_currency(self):
        # the budget's currency follows the account's
        self.apanel.load()
        self.apanel.budget = '42'
        self.apanel.currency_index = 12
        self.assertEqual(self.apanel.budget, '42.00')
    
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
        self.assertEqual(self.apanel.budget, '0.00')
    
    def test_fields_before_load(self):
        # ensure no crash occurs
        self.apanel.type_index
        self.apanel.budget
        self.apanel.budget_enabled
        self.apanel.budget_target_index
    
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
        self.assertEqual(self.apanel.budget, '42.00')
    

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
    

class AccountOfAllTypes(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_accounts_of_all_types()
    
    def test_available_budget_target(self):
        # The available budget targets are asset + liability
        self.apanel.load()
        self.assertEqual(self.apanel.available_budget_targets, ['asset', 'liability'])
    

class AccountWithBudgetTarget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_accounts_of_all_types()
        self.apanel.load() # this is 'expense'
        self.apanel.budget_target_index = 1 # 'liability'
        self.apanel.save()
    
    def test_delete_budget_target(self):
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.liabilities[0]
        self.bsheet.delete()
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        try:
            self.apanel.load()
        except ValueError:
            self.fail("When the target has been deleted, just select something else")
        self.assertEqual(self.apanel.budget_target_index, 0)
    
    def test_remember_budget_target(self):
        # budget target changes are remembered
        self.istatement.selected = self.istatement.income[0]
        self.apanel.load()
        self.assertEqual(self.apanel.budget_target_index, 0)
        self.istatement.selected = self.istatement.expenses[0]
        self.apanel.load()
        self.assertEqual(self.apanel.budget_target_index, 1)
    
