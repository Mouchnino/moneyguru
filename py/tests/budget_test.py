# coding: utf-8 
# Created By: Virgil Dupras
# Created On: 2009-06-02
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from .base import TestCase, CommonSetup
from ..model.account import EXPENSE, INCOME

class CommonSetup(CommonSetup):
    def setup_account_with_budget(self, is_expense=True, account_name='Some Expense'):
        # 4 days left to the month, 100$ monthly budget
        self.mock_today(2008, 1, 27)
        self.document.select_today_date_range()
        account_type = EXPENSE if is_expense else INCOME
        self.add_account(account_name, account_type=account_type)
        self.document.select_income_statement()
        if is_expense:
            self.istatement.select = self.istatement.expenses[0]
        else:
            self.istatement.select = self.istatement.income[0]
        self.set_budget('100')
    

class OneExpenseWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
    
    def test_budget_transactions(self):
        # When a budget is set budget transaction spawns show up in ttable, at the end of each month.
        self.document.select_transaction_table()
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
        self.document.select_transaction_table()
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
    