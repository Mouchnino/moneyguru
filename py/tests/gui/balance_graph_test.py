# Unit Name: moneyguru.gui.balance_graph_test
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date

from hsutil.currency import CAD

from ..base import TestCase, CommonSetup
from ...model.account import LIABILITY, EXPENSE

class TwoLiabilityTransactions(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account('Visa', account_type=LIABILITY)
        self.add_entry('3/1/2008', increase='120.00')
        self.add_entry('5/1/2008', decrease='40.00')
    
    def test_budget(self):
        # when we add a budget, the balance graph will show a regular progression throughout date range
        self.mock_today(2008, 1, 27)
        self.add_account('expense', account_type=EXPENSE)
        self.document.select_income_statement()
        self.istatement.select = self.istatement.expenses[0]
        self.set_budget('100') # 4 days left, 25$ each day
        self.document.select_balance_sheet()
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
        self.add_account('expense', account_type=EXPENSE)
        self.document.select_income_statement()
        self.istatement.select = self.istatement.expenses[0]
        self.set_budget('100')
        self.document.select_balance_sheet()
        self.document.select_next_date_range()
    
    def test_budget_with_future_txn(self):
        # when there's a future txn, we want the amount of that txn to be "sharply" displayed
        self.mock_today(2008, 1, 15)
        self.add_entry('20/1/2008', decrease='10')
        self.add_account('expense', account_type=EXPENSE)
        self.document.select_income_statement()
        self.istatement.select = self.istatement.expenses[0]
        self.set_budget('100') # 16 days left, 6.25$ per day
        self.document.select_balance_sheet()
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
        self.add_account('Visa', currency=CAD)
    
    def test_graph(self):
        self.assertEqual(self.balgraph.currency, CAD)
    
