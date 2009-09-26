# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from hsutil.currency import CAD, USD

from ..base import TestCase, CommonSetup, ApplicationGUI
from ...app import Application
from ...model.account import INCOME, EXPENSE
from ...model.date import MonthRange


class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_income_statement()
        self.check_gui_calls(self.istatement_gui, refresh=1)
    
    def test_add_account_in_other_groups(self):
        """When groups other than Assets are selected, new accounts go underneath it."""
        self.istatement.selected = self.istatement.expenses
        self.istatement.add_account()
        self.assertEqual(self.istatement.selected, self.istatement.expenses[0])
        self.istatement.add_account()
        self.assertEqual(self.istatement.selected, self.istatement.expenses[1])
        self.istatement.selected = self.istatement.income
        self.istatement.add_account()
        self.assertEqual(self.istatement.selected, self.istatement.income[0])
        self.istatement.add_account()
        self.assertEqual(self.istatement.selected, self.istatement.income[1])
        self.istatement.selected = None
        self.istatement.add_account()
        self.assertEqual(self.istatement.selected, self.istatement.income[2])
    
    def test_income_statement(self):
        """The income statement is empty"""
        self.assertEqual([x.name for x in self.istatement], ['INCOME', 'EXPENSES', 'NET INCOME'])
        

class AccountsAndEntries(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account_legacy('Account 1', account_type=INCOME)
        self.add_entry('10/01/2008', 'Entry 1', increase='100.00')
        self.add_entry('13/01/2008', 'Entry 2', increase='150.00')
        self.add_account_legacy('Account 2', account_type=INCOME)
        self.add_entry('11/12/2007', 'Entry 3', increase='100.00')
        self.add_entry('12/01/2008', 'Entry 4', decrease='20.00')
        self.mainwindow.select_income_statement()
    
    def test_add_entry(self):
        # adding an entry updates the cache flow (previously, the cache wouldn't be correctly invalidated)
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.add_entry('13/01/2008', 'Entry 3', increase='42.00')
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.income[0].cash_flow, '292.00')
    
    def test_attrs_with_budget(self):
        # Must include the budget. 250 of the 400 are spent, there's 150 left to add
        self.mock_today(2008, 1, 17)
        self.add_budget('Account 1', None, '400')
        self.mainwindow.select_income_statement()
        eq_(self.istatement.income[0].cash_flow, '250.00')
        eq_(self.istatement.income[0].budgeted, '150.00')
        eq_(self.istatement.income.budgeted, '150.00')
        eq_(self.istatement.net_income.budgeted, '150.00')
        self.document.select_next_date_range()
        eq_(self.istatement.income[0].cash_flow, '0.00')
        eq_(self.istatement.income[0].budgeted, '400.00')
        self.document.select_quarter_range()
        eq_(self.istatement.income[0].cash_flow, '250.00')
        eq_(self.istatement.income[0].budgeted, '950.00')
        self.document.select_year_range()
        eq_(self.istatement.income[0].cash_flow, '250.00')
        eq_(self.istatement.income[0].budgeted, '4550.00')
        self.document.select_year_to_date_range()
        eq_(self.istatement.income[0].cash_flow, '250.00')
    
    def test_cash_flow_with_underestimated_budget(self):
        self.mock_today(2008, 1, 17)
        self.add_budget('Account 1', None, '200')
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.income[0].cash_flow, '250.00')
    
    def test_exclude_account(self):
        # Excluding an account removes its amount from the totals and blanks its own amounts
        self.istatement.selected = self.istatement.income[1]
        self.istatement.toggle_excluded()
        self.assertEqual(self.istatement.income[1].cash_flow, '')
        self.assertEqual(self.istatement.income[1].last_cash_flow, '')
        self.assertEqual(self.istatement.income[1].delta, '')
        self.assertEqual(self.istatement.income[1].delta_perc, '')
        self.assertEqual(self.istatement.income.cash_flow, '250.00')
        self.assertEqual(self.istatement.income.last_cash_flow, '0.00')
        self.assertEqual(self.istatement.income.delta, '250.00')
        self.assertEqual(self.istatement.income.delta_perc, '---')
    
    def test_income_statement(self):
        self.assertEqual(self.document.date_range, MonthRange(date(2008, 1, 1)))
        self.assertEqual(self.istatement.income[0].name, 'Account 1')
        self.assertEqual(self.istatement.income[0].cash_flow, '250.00')
        self.assertEqual(self.istatement.income[1].name, 'Account 2')
        self.assertEqual(self.istatement.income[1].cash_flow, '-20.00')
        self.assertEqual(self.istatement.income.cash_flow, '230.00')
    
    def test_set_custom_date_range(self):
        # same problem as test_year_to_date_last_cash_flow
        self.document.select_custom_date_range()
        self.cdrpanel.start_date = '01/01/2008'
        self.cdrpanel.start_date = '12/12/2008'
        self.cdrpanel.ok()
        self.assertEqual(self.istatement.income[0].last_cash_flow, '0.00')
    
    def test_year_to_date_last_cash_flow(self):
        # When the YTD range is selected, the "Last" column shows last year's value (here, 0) instead
        # of showing the exact same thing as this period.
        self.mock_today(2008, 12, 12)
        self.document.select_year_to_date_range()
        self.assertEqual(self.istatement.income[0].last_cash_flow, '0.00')
    

class MultipleCurrencies(TestCase):
    def setUp(self):
        self.app = Application(ApplicationGUI(), default_currency=CAD)
        self.create_instances()
        self.document.select_month_range()
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        USD.set_CAD_value(0.9, date(2008, 1, 31))
        self.add_group('Group', account_type=INCOME)
        self.add_account_legacy('CAD account', currency=CAD, account_type=INCOME, group_name='Group')
        self.add_entry('1/1/2008', 'USD entry', increase='100.00')
        self.add_account_legacy('USD account', currency=USD, account_type=INCOME, group_name='Group')
        self.add_entry('1/1/2007', 'USD entry', increase='50.00')
        self.add_entry('1/1/2008', 'USD entry', increase='80.00')
        self.add_entry('31/1/2008', 'USD entry', increase='20.00')
        self.mainwindow.select_income_statement()
    
    def test_with_budget(self):
        # What this test is making sure of is that the account's budget is of the same currency than
        # the account itself
        self.mock_today(2008, 1, 20)
        self.add_budget('USD account', None, '300usd')
        self.mainwindow.select_income_statement()
        eq_(self.istatement.income[0][1].cash_flow, 'USD 100.00')
        eq_(self.istatement.income[0][1].budgeted, 'USD 200.00')
    
    def test_income_statement(self):
        """Each income/expense transaction is converted using the day's rate."""
        self.assertEqual(self.document.date_range, MonthRange(date(2008, 1, 1)))
        self.assertEqual(self.istatement.income[0][0].cash_flow, '100.00')
        self.assertEqual(self.istatement.income[0][1].cash_flow, 'USD 100.00')
        self.assertEqual(self.istatement.income[0].cash_flow, '182.00')   # 80 * .8 + 20 * .9 + 100
        self.assertEqual(self.istatement.income.cash_flow, '182.00')
    

class MultipleCurrenciesOverTwoMonths(TestCase):
    def setUp(self):
        self.app = Application(ApplicationGUI(), default_currency=CAD)
        self.create_instances()
        self.document.select_month_range()
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        USD.set_CAD_value(0.9, date(2008, 1, 31))
        USD.set_CAD_value(0.9, date(2008, 2, 10))
        self.add_account_legacy('CAD account', currency=CAD, account_type=INCOME)
        self.add_entry('1/1/2008', 'CAD entry', increase='200.00')
        self.add_entry('1/2/2008', 'CAD entry', increase='190.00')
        self.add_account_legacy('USD account', currency=USD, account_type=EXPENSE)
        self.add_entry('1/1/2008', 'USD entry', increase='50.00')
        self.add_entry('1/1/2008', 'USD entry', increase='80.00')
        self.add_entry('31/1/2008', 'USD entry', increase='20.00')
        self.add_entry('10/2/2008', 'USD entry', increase='100.00')
        self.mainwindow.select_income_statement()
    
    def test_income_statement(self):
        # the last_cach_flow and deltas are correct
        self.assertEqual(self.istatement.income[0].cash_flow, '190.00')
        self.assertEqual(self.istatement.income[0].last_cash_flow, '200.00')
        self.assertEqual(self.istatement.income[0].delta, '-10.00')
        self.assertEqual(self.istatement.income[0].delta_perc, '-5.0%')
        self.assertEqual(self.istatement.expenses[0].cash_flow, 'USD 100.00')
        self.assertEqual(self.istatement.expenses[0].last_cash_flow, 'USD 150.00')
        self.assertEqual(self.istatement.expenses[0].delta, 'USD -50.00')
        self.assertEqual(self.istatement.expenses[0].delta_perc, '-33.3%')
        self.assertEqual(self.istatement.expenses.cash_flow, '90.00')   # 100 * .9
        self.assertEqual(self.istatement.expenses.last_cash_flow, '122.00')   # 130 * .8 + 20 * .9
        self.assertEqual(self.istatement.expenses.delta, '-32.00')   # 130 * .8 + 20 * .9
        self.assertEqual(self.istatement.expenses.delta_perc, '-26.2%')
        self.assertEqual(self.istatement.net_income.cash_flow, '100.00') 
        self.assertEqual(self.istatement.net_income.last_cash_flow, '78.00')
        self.assertEqual(self.istatement.net_income.delta, '22.00')
        self.assertEqual(self.istatement.net_income.delta_perc, '+28.2%')
    

class EntriesSpreadOverAYear(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('Account', account_type=INCOME)
        self.add_entry('01/01/2007', 'Entry', increase='1')
        self.add_entry('01/04/2007', 'Entry', increase='2')
        self.add_entry('01/08/2007', 'Entry', increase='3')
        self.add_entry('01/12/2007', 'Entry', increase='4')
        self.add_entry('01/01/2008', 'Entry', increase='5')
        self.add_entry('01/04/2008', 'Entry', increase='6')
        self.add_entry('01/08/2008', 'Entry', increase='7')
        self.add_entry('01/12/2008', 'Entry', increase='8')
        self.add_entry('01/03/2009', 'Entry', increase='9')
        self.add_entry('01/05/2009', 'Entry', increase='10')
        self.mainwindow.select_income_statement()
    
    def test_select_running_year_range(self):
        # the 'Last' column will correctly be set and will include amounts from a whole year before
        # the start of the running year.
        self.mock_today(2008, 12, 1)
        self.document.select_running_year_range()
        # ahead_months is 2, so current is 01/03/2008-28/02/2009, which means 6 + 7 + 8 (21)
        self.assertEqual(self.istatement.income[0].cash_flow, '21.00')
        # 'Last' is 01/03/2007-28/02/2008, which means 2 + 3 + 4 + 5 (14)
        self.assertEqual(self.istatement.income[0].last_cash_flow, '14.00')
    
