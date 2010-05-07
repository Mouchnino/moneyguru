# Created By: Virgil Dupras
# Created On: 2008-08-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from hsutil.currency import CAD

from ..base import TestCase
from ...model.account import AccountType

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.drsel.select_month_range()
    
    def test_cook_bar_overflow(self):
        # When some data is included in a bar that overflows, we must not forget to ensure cooking
        # until the end of the *overflow*, not the end of the date range.
        self.add_account('Checking')
        self.add_account('Income', account_type=AccountType.Income)
        self.mainwindow.show_account()
        self.add_entry('01/11/2008', transfer='Checking', increase='42') #sunday
        self.drsel.select_prev_date_range() # oct 2008
        self.add_entry('31/10/2008', transfer='Checking', increase='42')
        # now, the creation of the txn forced a recook. what we want to make sure is that both 
        # entries will be in the bar
        eq_(self.bar_graph_data()[0][2], '84.00')
    

class ForeignAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Visa', account_type=AccountType.Income, currency=CAD)
        self.mainwindow.show_account()
    
    def test_graph(self):
        eq_(self.bargraph.currency, CAD)
    

class SomeIncomeInTheFutureWithRangeOnYearToDate(TestCase):
    def setUp(self):
        self.mock_today(2010, 1, 12)
        self.create_instances()
        self.add_account('Checking')
        self.mainwindow.show_account()
        self.add_entry('13/01/2010', transfer='Income', increase='42')
        self.drsel.select_year_to_date_range()
    
    def test_bar_graphs_during_ytd_dont_show_future_data(self):
        # Unlike all other date ranges, bar charts during YTD don't overflow
        self.mainwindow.select_income_statement()
        eq_(len(self.pgraph.data), 0)
    

class SomeIncomeTodayAndInTheFuture(TestCase):
    def setUp(self):
        self.mock_today(2010, 1, 12)
        self.create_instances()
        self.add_account('Checking')
        self.add_account('Income', account_type=AccountType.Income)
        self.mainwindow.show_account()
        self.add_entry('13/01/2010', transfer='Checking', increase='12')
        self.add_entry('12/01/2010', transfer='Checking', increase='30')
        self.drsel.select_year_range()
    
    def test_bar_split_in_two(self):
        # when some amounts are in the future, but part of the same bar, the amounts are correctly
        # split in the data point
        eq_(self.bargraph.data[0][2:], (30, 12))
    

class AccountAndEntriesAndBudget(TestCase):
    def setUp(self):
        # Weeks of Jan: 31-6 7-13 14-20 21-27 28-3
        self.create_instances()
        self.drsel.select_month_range()
        self.add_account('Account 1', account_type=AccountType.Income)
        self.mock_today(2008, 1, 17)
        self.add_budget('Account 1', None, '400')
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.add_entry('10/01/2008', 'Entry 1', increase='100.00')
        self.add_entry('14/01/2008', 'Entry 2', increase='150.00')
    
    def test_cash_flow_with_budget(self):
        # Must include the budget. 250 of the 400 are spent, there's 150 left to add proportionally
        # in the remaining weeks.
        eq_(self.bargraph.data[0][2:], (100, 0)) # week 2
        # there are 14 days left, week 3 contains 3 of them. Therefore, the budget amount is
        # (150 / 14) * 3 --> 32.14
        eq_(self.bargraph.data[1][2:], (150, 32.14)) # week 3
    

class RunningYearWithSomeIncome(TestCase):
    def setUp(self):
        self.mock_today(2008, 11, 1)
        self.create_instances()
        self.add_account('Checking')
        self.mainwindow.show_account()
        self.add_entry('11/09/2008', transfer='Income', increase='42')
        self.add_entry('24/09/2008', transfer='Income', increase='44')
        self.drsel.select_running_year_range()
    
    def test_data_is_taken_from_shown_account(self):
        # Ensure that bargraph's data is taken from shown_account, *not* selected_account
        self.mainwindow.select_transaction_table()
        self.add_txn('23/09/2008', from_='something else', to='Checking', amount='1')
        self.ttable.select([0])
        self.ttable.show_from_account()
        # shown: Income selected: Checking
        eq_(self.bargraph.title, 'Income')
        eq_(self.bar_graph_data()[0][2], '86.00') # *not* 87, like what would show with Checking
    
    def test_monthly_bars(self):
        # with the running year range, the bars are monthly
        self.mainwindow.select_income_statement()
        eq_(len(self.pgraph.data), 1) # there is only one bar
    
