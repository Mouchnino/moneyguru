# coding: utf-8 
# Unit Name: moneyguru.budget_test
# Created By: Virgil Dupras
# Created On: 2009-06-02
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date

from .base import TestCase, CommonSetup
from ..model.account import EXPENSE

class CommonSetup(CommonSetup):
    def setup_one_expense_with_budget(self):
        # 4 days left to the month, 100$ monthly budget
        self.mock_today(2008, 1, 27)
        self.document.select_today_date_range()
        self.add_account('Some Expense', account_type=EXPENSE)
        self.document.select_income_statement()
        self.istatement.select = self.istatement.expenses[0]
        self.set_budget('100')
    
class OneExpenseWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_expense_with_budget()
    
    def test_budget_transactions(self):
        # When a budget is set budget transaction spawns show up in ttable, on the 1st of every month.
        # We are in a yearly view, in january, so there's 11 budget txn coming.
        self.document.select_transaction_table()
        self.assertEqual(len(self.ttable), 11)
        self.assertEqual(self.ttable[0].amount, '100.00')
        self.assertEqual(self.ttable[0].date, '01/02/2008')
        self.assertEqual(self.ttable[10].date, '01/12/2008')
     

class OneExpenseWithBudgetAndTxn(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_expense_with_budget()
        self.add_txn(date='27/01/2008', to='Some Expense', amount='42')
    
    def test_budget_transaction_is_adjusted(self):
        # Adding a transaction affects the next budget transaction
        self.assertEqual(self.ttable[1].amount, '58.00')
        self.assertEqual(self.ttable[2].amount, '100.00')
    

class OneExpenseWithBustedBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_expense_with_budget()
        self.add_txn(date='27/01/2008', to='Some Expense', amount='142')
    
    def test_budget_spawn_doesnt_show(self):
        # When a busget is busted, don't show the spawn
        self.assertEqual(len(self.ttable), 11)
        self.assertEqual(self.ttable[1].date, '01/03/2008')
    