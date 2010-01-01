# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from hsutil.currency import CAD

from ..base import TestCase, CommonSetup
from ...model.account import LIABILITY, EXPENSE, INCOME

class TwoLiabilityTransactions(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account_legacy('Visa', account_type=LIABILITY)
        self.add_entry('3/1/2008', increase='120.00')
        self.add_entry('5/1/2008', decrease='40.00')
    
    def test_budget(self):
        # when we add a budget, the balance graph will show a regular progression throughout date range
        self.mock_today(2008, 1, 27)
        self.add_account_legacy('expense', account_type=EXPENSE)
        self.add_budget('expense', 'Visa', '100')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.liabilities[0]
        self.bsheet.show_selected_account()
        expected = [('04/01/2008', '120.00'), ('05/01/2008', '120.00'), ('06/01/2008', '80.00'), 
            ('28/01/2008', '80.00'), ('01/02/2008', '180.00')]
        self.assertEqual(self.graph_data(), expected)
        self.document.select_next_date_range()
        self.assertEqual(self.graph_data()[0], ('01/02/2008', '180.00'))
    
    def test_budget_on_last_day_of_the_range(self):
        # don't raise a ZeroDivizionError
        self.mock_today(2008, 1, 31)
        self.add_account_legacy('expense', account_type=EXPENSE)
        self.add_budget('expense', 'Visa', '100')
        self.mainwindow.select_balance_sheet()
        self.document.select_next_date_range()
    
    def test_budget_with_future_txn(self):
        # when there's a future txn, we want the amount of that txn to be "sharply" displayed
        self.mock_today(2008, 1, 15)
        self.add_entry('20/1/2008', decrease='10')
        self.add_account_legacy('expense', account_type=EXPENSE)
        self.add_budget('expense', 'Visa', '100')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.liabilities[0]
        self.bsheet.show_selected_account()
        # the amount at the 20th is supposed to include budgeting for the 20th, and the 21st data point
        # has to include budget for the 21st
        expected = [('04/01/2008', '120.00'), ('05/01/2008', '120.00'), ('06/01/2008', '80.00'), 
            ('16/01/2008', '80.00'), ('20/01/2008', '105.00'), ('21/01/2008', '101.25'), ('01/02/2008', '170.00')]
        self.assertEqual(self.graph_data(), expected)
    
    def test_graph(self):
        expected = [('04/01/2008', '120.00'), ('05/01/2008', '120.00'), 
                    ('06/01/2008', '80.00'), ('01/02/2008', '80.00')]
        self.assertEqual(self.graph_data(), expected)
        self.assertEqual(self.balgraph.title, 'Visa')
    

class ForeignAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('Visa', currency=CAD)
    
    def test_graph(self):
        self.assertEqual(self.balgraph.currency, CAD)
    

class BudgetAndNoTranaction(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.mock_today(2008, 1, 1)
        self.document.select_month_range()
        self.document.select_today_date_range()
        self.add_account_legacy('asset')
        self.add_account_legacy('income', account_type=INCOME)
        self.add_budget('income', 'asset', '100')
    
    def test_future_date_range(self):
        # There was a bug where when in a future date range, and also in a range with no transaction,
        # no budget data would be drawn.
        self.document.select_next_date_range()
        self.mainwindow.select_balance_sheet()
        # Now, we're supposed to see a graph starting at 100 and ending at 200
        expected = [('01/02/2008', '100.00'), ('01/03/2008', '200.00')]
        eq_(self.nw_graph_data(), expected)
    
