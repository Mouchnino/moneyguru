# coding: utf-8 
# Created By: Virgil Dupras
# Created On: 2009-06-02
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..model.account import INCOME
from .base import TestCase, CommonSetup

class OneExpenseWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
    
    def test_budget_transactions(self):
        # When a budget is set budget transaction spawns show up in ttable, at the end of each month.
        self.mainwindow.select_transaction_table()
        self.assertEqual(len(self.ttable), 12)
        self.assertEqual(self.ttable[0].amount, '100.00')
        self.assertEqual(self.ttable[0].date, '31/01/2008')
        self.assertEqual(self.ttable[0].to, 'Some Expense')
        self.assertEqual(self.ttable[11].date, '31/12/2008')
     

class OneIncomeWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget(is_expense=False, account_name='Some Income')
    
    def test_budget_amount_flow_direction(self):
        # When the budgeted account is an income, the account gets in the *from* column
        self.mainwindow.select_transaction_table()
        self.assertEqual(self.ttable[0].from_, 'Some Income')
    
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
        self.add_account('some asset')
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
    

class TwoBudgetsFromSameAccount(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account('income', account_type=INCOME)
        self.add_entry(increase='25') # This entry must not be counted twice in budget calculations!
        self.add_budget('income', None, '100')
        self.add_budget('income', None, '100')
    
    def test_both_budgets_are_counted(self):
        # The amount budgeted is the sum of all budgets, not just the first one.
        self.mainwindow.select_income_statement()
        eq_(self.istatement.income[0].cash_flow, '200.00')
    
