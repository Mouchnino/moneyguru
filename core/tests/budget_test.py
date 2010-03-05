# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-06-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..model.account import AccountType
from .base import TestCase, CommonSetup, TestSaveLoadMixin

class OneIncomeWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget(is_expense=False, account_name='Some Income')
    
    def test_budget_amount_flow_direction(self):
        # When the budgeted account is an income, the account gets in the *from* column
        self.mainwindow.select_transaction_table()
        self.assertEqual(self.ttable[0].from_, 'Some Income')
    
    def test_dont_replace_split_instances_needlessly(self):
        # The bug was that during budget cooking, all spawns, including those before the cooked date
        # range, would have their split re-created with new amounts. Because of this, going back in
        # the date range would cause cached entries to be "bumped out" of the transaction. This
        # would result in the shown account to be displayed in the "Transfer" column.
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        eq_(self.etable[0].transfer, '')
        self.document.select_next_date_range()
        self.document.select_prev_date_range()
        eq_(self.etable[0].transfer, '') # It shouldn't be set to "Some Income"
    
    def test_save_and_load(self):
        # There was a crash when loading a targetless budget
        self.document = self.save_and_load() # no crash
        self.create_instances()
        self.mainwindow.select_budget_table()
        eq_(len(self.btable), 1)
    
    def test_set_budget_again(self):
        # There was a bug where setting the amount on a budget again wouldn't invert that amount
        # in the case of an income-based budget.
        self.mainwindow.select_budget_table()
        self.btable.select([0])
        self.mainwindow.edit_item()
        self.bpanel.amount = '200'
        self.bpanel.save()
        self.mainwindow.select_transaction_table()
        self.assertEqual(self.ttable[0].from_, 'Some Income')
    

class OneIncomeWithBudgetInPast(TestCase):
    def setUp(self):
        self.mock_today(2009, 11, 16)
        self.create_instances()
        self.add_account('income', account_type=AccountType.Income)
        self.add_budget('income', None, '100', start_date='01/09/2009')
    
    def test_spawns_dont_linger(self):
        # If the budget hasn't been spent in the past, we don't continue to spawn transactions for
        # it once we went past the spawn's end date.
        self.mainwindow.select_transaction_table()
         # Only the spawns for november and december, NOT, september and october.
        eq_(len(self.ttable), 2)
    

class OneExpenseWithBudgetAndTxn(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
        self.add_txn(date='27/01/2008', to='Some Expense', amount='42')
    
    def test_budget_transaction_is_adjusted(self):
        # Adding a transaction affects the next budget transaction
        self.assertEqual(self.ttable[1].amount, '58.00')
        self.assertEqual(self.ttable[2].amount, '100.00')
    

class OneExpenseWithBustedBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
        self.add_txn(date='27/01/2008', to='Some Expense', amount='142')
    
    def test_budget_spawn_doesnt_show(self):
        # When a budget is busted, don't show the spawn
        self.assertEqual(len(self.ttable), 12)
        self.assertEqual(self.ttable[1].date, '29/02/2008')
    

class OneExpenseWithBudgetAndTarget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('some asset')
        self.setup_account_with_budget(target_name='some asset')
    
    def test_asset_is_in_the_from_column(self):
        # In the budget transaction, 'some asset' is in the 'from' column.
        self.mainwindow.select_transaction_table()
        eq_(self.ttable[0].from_, 'some asset')
    
    def test_budget_is_counted_in_etable_balance(self):
        # When an asset is a budget target, its balance is correctly incremented in the etable.
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        # The balance of the budget entry has a correctly decremented balance (the budget is an expense).
        eq_(self.etable[0].balance, '-100.00')
    
    def test_delete_account(self):
        # When deleting an income or expense account, delete all budgets associated with it as well.
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        self.istatement.delete()
        self.arpanel.ok() # don't reassign
        self.mainwindow.select_budget_table()
        eq_(len(self.btable), 0) # the budget has been removed
    
    def test_delete_account_and_reassign(self):
        # When reassigning an account on deletion, change budgets instead of deleting it.
        self.add_account_legacy('other expense', account_type=AccountType.Expense)
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses[1] # Some Expense
        self.istatement.delete()
        self.arpanel.account_index = 2 # other expense
        self.arpanel.ok()
        self.mainwindow.select_budget_table()
        eq_(self.btable[0].account, 'other expense')
    
    def test_delete_target(self):
        # When deleting the target account, budgets having this account as their target have it
        # changed to None
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.arpanel.ok()
        self.mainwindow.select_budget_table()
        eq_(self.btable[0].target, '') # been changed to None
    
    def test_delete_target_and_reassign(self):
        # When reassigning an account on deletion, change budgets' target.
        self.add_account_legacy('other asset')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # some asset
        self.bsheet.delete()
        self.arpanel.account_index = 1 # other asset
        self.arpanel.ok()
        self.mainwindow.select_budget_table()
        eq_(self.btable[0].target, 'other asset')
    

class TwoBudgetsFromSameAccount(TestCase):
    def setUp(self):
        # XXX this mock is because the test previously failed because we were currently on the last
        # day of the month. TODO: Re-create the last-day condition and fix the calculation bug
        self.mock_today(2009, 8, 20)
        self.create_instances()
        self.document.select_month_range()
        self.add_account_legacy('income', account_type=AccountType.Income)
        self.add_entry(increase='25') # This entry must not be counted twice in budget calculations!
        self.add_budget('income', None, '100')
        self.add_budget('income', None, '100')
    
    def test_both_budgets_are_counted(self):
        # The amount budgeted is the sum of all budgets, not just the first one.
        self.mainwindow.select_income_statement()
        eq_(self.istatement.income[0].budgeted, '175.00')
    

class YearBudgetWithEntryBeforeCurrentMonth(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2009, 8, 24)
        self.document.select_year_range()
        self.add_account_legacy('income', account_type=AccountType.Income)
        self.add_entry(date='01/07/2009', increase='25')
        self.add_budget('income', None, '100', start_date='01/01/2009', repeat_type_index=3) # yearly
    
    def test_entry_is_correctly_counted_in_budget(self):
        # The entry, although not in the current month, is counted in budget calculations
        self.mainwindow.select_income_statement()
        eq_(self.istatement.income[0].budgeted, '75.00')
    
    def test_spawn_has_correct_date(self):
        # The spawn is created at the correct date, which is at the end of the year
        self.mainwindow.select_transaction_table()
        # first txn is the entry on 01/07
        eq_(self.ttable[1].date, '31/12/2009')
    

class ScheduledTxnAndBudget(TestCase, CommonSetup):
    def setUp(self):
        self.mock_today(2009, 9, 10)
        self.create_instances()
        self.document.select_month_range()
        self.add_account_legacy('account', account_type=AccountType.Expense)
        self.setup_scheduled_transaction(start_date='10/09/2009', account='account', debit='1',
            repeat_type_index=2) # monthly
        self.add_budget('account', None, '10') # monthly
    
    def test_schedule_affects_budget(self):
        # schedule spawns affect the budget spawns
        self.mainwindow.select_transaction_table()
        eq_(self.ttable[1].amount, '9.00') # 1$ has been removed from the budgeted 10
    

class YearlyBudgetWithStartDateStopDateInterval(TestCase, TestSaveLoadMixin):
    # TestSaveLoadMixin: to make sure that all budget fields are correctly saved
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('income', account_type=AccountType.Income)
        self.add_budget('income', None, '100', start_date='01/01/2009', repeat_type_index=3,
            repeat_every=2, stop_date='01/01/2022')
    
