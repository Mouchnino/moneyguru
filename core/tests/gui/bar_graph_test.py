# Created By: Virgil Dupras
# Created On: 2008-08-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_
from hscommon.currency import CAD

from ..base import TestApp, with_app
from ...model.account import AccountType

class TestPristine:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        return app
    
    @with_app(do_setup)
    def test_cook_bar_overflow(self, app):
        # When some data is included in a bar that overflows, we must not forget to ensure cooking
        # until the end of the *overflow*, not the end of the date range.
        app.add_account('Checking')
        app.add_account('Income', account_type=AccountType.Income)
        app.mainwindow.show_account()
        app.add_entry('01/11/2008', transfer='Checking', increase='42') #sunday
        app.drsel.select_prev_date_range() # oct 2008
        app.add_entry('31/10/2008', transfer='Checking', increase='42')
        # now, the creation of the txn forced a recook. what we want to make sure is that both 
        # entries will be in the bar
        eq_(app.bar_graph_data()[0][2], '84.00')
    

class TestForeignAccount:
    def do_setup(self):
        app = TestApp()
        app.add_account('Visa', account_type=AccountType.Income, currency=CAD)
        app.mainwindow.show_account()
        return app
    
    @with_app(do_setup)
    def test_graph(self, app):
        eq_(app.bargraph.currency, CAD)
    

class TestSomeIncomeInTheFutureWithRangeOnYearToDate:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2010, 1, 12)
        app = TestApp()
        app.add_account('Checking')
        app.mainwindow.show_account()
        app.add_entry('13/01/2010', transfer='Income', increase='42')
        app.drsel.select_year_to_date_range()
        return app
    
    @with_app(do_setup)
    def test_bar_graphs_during_ytd_dont_show_future_data(self, app):
        # Unlike all other date ranges, bar charts during YTD don't overflow
        app.mainwindow.select_income_statement()
        eq_(len(app.pgraph.data), 0)
    

class TestSomeIncomeTodayAndInTheFuture:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2010, 1, 12)
        app = TestApp()
        app.add_account('Checking')
        app.add_account('Income', account_type=AccountType.Income)
        app.mainwindow.show_account()
        app.add_entry('13/01/2010', transfer='Checking', increase='12')
        app.add_entry('12/01/2010', transfer='Checking', increase='30')
        app.drsel.select_year_range()
        return app
    
    @with_app(do_setup)
    def test_bar_split_in_two(self, app):
        # when some amounts are in the future, but part of the same bar, the amounts are correctly
        # split in the data point
        eq_(app.bargraph.data[0][2:], (30, 12))
    

class TestAccountAndEntriesAndBudget:
    def do_setup(self, monkeypatch):
        # Weeks of Jan: 31-6 7-13 14-20 21-27 28-3
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account('Account 1', account_type=AccountType.Income)
        monkeypatch.patch_today(2008, 1, 17)
        app.add_budget('Account 1', None, '400')
        app.mainwindow.select_income_statement()
        app.istatement.selected = app.istatement.income[0]
        app.istatement.show_selected_account()
        app.add_entry('10/01/2008', 'Entry 1', increase='100.00')
        app.add_entry('14/01/2008', 'Entry 2', increase='150.00')
        return app
    
    @with_app(do_setup)
    def test_cash_flow_with_budget(self, app):
        # Must include the budget. 250 of the 400 are spent, there's 150 left to add proportionally
        # in the remaining weeks.
        eq_(app.bargraph.data[0][2:], (100, 0)) # week 2
        # there are 14 days left, week 3 contains 3 of them. Therefore, the budget amount is
        # (150 / 14) * 3 --> 32.14
        eq_(app.bargraph.data[1][2:], (150, 32.14)) # week 3
    

class TestRunningYearWithSomeIncome:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2008, 11, 1)
        app = TestApp()
        app.add_account('Checking')
        app.mainwindow.show_account()
        app.add_entry('11/09/2008', transfer='Income', increase='42')
        app.add_entry('24/09/2008', transfer='Income', increase='44')
        app.drsel.select_running_year_range()
        return app
    
    @with_app(do_setup)
    def test_data_is_taken_from_shown_account(self, app):
        # Ensure that bargraph's data is taken from shown_account, *not* selected_account
        app.mainwindow.select_transaction_table()
        app.add_txn('23/09/2008', from_='something else', to='Checking', amount='1')
        app.ttable.select([0])
        app.ttable.show_from_account()
        # shown: Income selected: Checking
        eq_(app.bargraph.title, 'Income')
        eq_(app.bar_graph_data()[0][2], '86.00') # *not* 87, like what would show with Checking
    
    @with_app(do_setup)
    def test_monthly_bars(self, app):
        # with the running year range, the bars are monthly
        app.mainwindow.select_income_statement()
        eq_(len(app.pgraph.data), 1) # there is only one bar
    
