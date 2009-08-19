# Created By: Virgil Dupras
# Created On: 2008-09-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from datetime import date

from hsutil.currency import Currency, USD, CAD

from ..base import TestCase, CallLogger, CommonSetup
from ...app import Application
from ...gui.pie_chart import SLICE_COUNT
from ...model.account import LIABILITY, INCOME

class _SomeAssetsAndLiabilities(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.mock_today(2009, 1, 29) # On the last day of the month, some tests fail
        self.add_account('a1')
        self.add_entry(increase='1.01') # values are trucated
        self.add_account('a2')
        self.add_entry(increase='4')
        self.add_account('a3')
        self.add_entry(increase='2')
        self.add_account('a4')
        self.add_entry(increase='3')
        self.add_account('empty') # doesn't show
        self.add_account('l1', account_type=LIABILITY)
        self.add_entry(increase='3')
        self.add_account('l2', account_type=LIABILITY)
        self.add_entry(increase='5')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets
        self.clear_gui_calls()
    

class SomeAssetsAndLiabilities(_SomeAssetsAndLiabilities):
    def setUp(self):
        _SomeAssetsAndLiabilities.setUp(self)
    
    def test_asset_pie_chart_values(self):
        # The asset pie chart values are sorted in reversed order of amount and have correct titles
        self.assertEqual(self.apie.title, 'Assets')
        expected = [
            ('a2 40.0%', 4),
            ('a4 30.0%', 3),
            ('a3 20.0%', 2),
            ('a1 10.1%', 1.01),
        ]
        self.assertEqual(self.apie.data, expected)
    
    def test_budget_multiple_currency(self):
        # just make sure it doesn't crash
        self.bsheet.selected = self.bsheet.assets[0]
        self.apanel.load()
        self.apanel.currency_index = Currency.all.index(CAD)
        self.apanel.save()
        self.add_account('income', account_type=INCOME)
        self.mainwindow.select_income_statement()
        self.set_budget('5', 0) # target: a1
        self.mainwindow.select_balance_sheet() # don't crash
    
    def test_exclude_account(self):
        # excluding an account removes it from the pie chart
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.toggle_excluded()
        expected = [
            ('a2 44.4%', 4),
            ('a4 33.3%', 3),
            ('a3 22.2%', 2),
        ]
        self.assertEqual(self.apie.data, expected)
        self.check_gui_calls(self.apie_gui, refresh=1)
    
    def test_liabilities_pie(self):
        # the lpie also works
        self.assertEqual(self.lpie.title, 'Liabilities')
        expected = [
            ('l2 62.5%', 5),
            ('l1 37.5%', 3),
        ]
        self.assertEqual(self.lpie.data, expected)
    

class SomeAssetsAndLiabilitiesWithBudget(_SomeAssetsAndLiabilities):
    def setUp(self):
        _SomeAssetsAndLiabilities.setUp(self)
        self.document.select_today_date_range()
        self.add_account('income', account_type=INCOME)
        self.set_budget('5', 2) # target: a3
        self.mainwindow.select_balance_sheet()
    
    def test_future_date_range(self):
        # the budget amounts used for the pie chart include all previous budgets
        self.document.select_next_date_range()
        expected = [
            ('a3 60.0%', 12),
            ('a2 20.0%', 4),
            ('a4 15.0%', 3),
            ('a1 5.0%', 1.01),
        ]
        self.assertEqual(self.apie.data, expected)
    
    def test_pie_values(self):
        # budgeted amounts are also reflected in the pie chart
        expected = [
            ('a3 46.6%', 7),
            ('a2 26.6%', 4),
            ('a4 20.0%', 3),
            ('a1 6.7%', 1.01),
        ]
        self.assertEqual(self.apie.data, expected)
    

class MoreThanSliceCountAssets(TestCase):
    def setUp(self):
        self.create_instances()
        for i in range(SLICE_COUNT + 2):
            self.add_account('account %d' % i)
            self.add_entry(increase='1')
        self.mainwindow.select_balance_sheet()
    
    def test_assets_pie_chart_values(self):
        # The pie chart values are sorted in reversed order of amount and have correct titles
        data = self.apie.data
        self.assertEqual(len(data), SLICE_COUNT)
        other = data[-1]
        self.assertEqual(other, ('Others %1.1f%%' % (3 / (SLICE_COUNT + 2) * 100), 3))
    

class SomeIncomeAndExpenses(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account('foo')
        self.add_entry(transfer='i1', increase='2')
        self.add_entry(transfer='i2', increase='4')
        self.add_entry(transfer='i3', increase='1')
        self.add_entry(transfer='i4', increase='3')
        self.add_entry(transfer='e1', decrease='3')
        self.add_entry(transfer='e2', decrease='1')
        self.add_entry(transfer='e3', decrease='4')
        self.add_entry(transfer='e4', decrease='2')
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses
        self.clear_gui_calls()
    
    def test_budget(self):
        # budgeted amounts are also reflected in the pie chart
        self.mock_today(2009, 1, 29) # On the last day of the month, this test fails
        self.istatement.selected = self.istatement.expenses[0]
        self.set_budget('5')
        expected = [
            ('e1 41.7%', 5),
            ('e3 33.3%', 4),
            ('e4 16.7%', 2),
            ('e2 8.3%', 1),
        ]
        self.assertEqual(self.epie.data, expected)
    
    def test_expenses_pie_chart_values(self):
        # The expenses pie chart values are sorted in reversed order of amount and have correct titles
        self.assertEqual(self.epie.title, 'Expenses')
        expected = [
            ('e3 40.0%', 4),
            ('e1 30.0%', 3),
            ('e4 20.0%', 2),
            ('e2 10.0%', 1),
        ]
        self.assertEqual(self.epie.data, expected)
    
    def test_exclude_account(self):
        # excluding an account removes it from the pie chart
        self.istatement.selected = self.istatement.expenses[0]
        self.istatement.toggle_excluded()
        expected = [
            ('e3 57.1%', 4),
            ('e4 28.6%', 2),
            ('e2 14.3%', 1),
        ]
        self.assertEqual(self.epie.data, expected)
        self.check_gui_calls(self.epie_gui, refresh=1)
    
    def test_income_pie(self):
        # the ipie also works
        self.istatement.selected = self.istatement.income[0]
        self.assertEqual(self.ipie.title, 'Income')
        expected = [
            ('i2 40.0%', 4),
            ('i4 30.0%', 3),
            ('i1 20.0%', 2),
            ('i3 10.0%', 1),
        ]
        self.assertEqual(self.ipie.data, expected)
    

class DifferentDateRanges(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account('foo')
        self.add_entry(date='01/08/2008', transfer='baz', increase='5')
        self.add_entry(date='01/08/2008', transfer='bar', decrease='1')
        self.add_entry(date='01/09/2008', transfer='bar', decrease='2')
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
    
    def test_balance_pie_chart(self):
        # the data in the balance pie chart reflects the currencly selected date range
        self.assertEqual(self.apie.data, [('foo 100.0%', 2)])
        self.document.select_prev_date_range()
        self.assertEqual(self.apie.data, [('foo 100.0%', 4)])
        self.check_gui_calls(self.apie_gui, refresh=1)
    
    def test_cash_flow_pie_chart(self):
        # the data in the cash flow pie chart reflects the currencly selected date range
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        self.clear_gui_calls()
        self.assertEqual(self.epie.data, [('bar 100.0%', 2)])
        self.document.select_prev_date_range()
        self.assertEqual(self.epie.data, [('bar 100.0%', 1)])
        self.check_gui_calls(self.epie_gui, refresh=1)
    

class MultipleCurrencies(TestCase):
    def setUp(self):
        self.app = Application(CallLogger(), default_currency=CAD)
        self.create_instances()
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        self.add_account('USD income', account_type=INCOME, currency=USD)
        self.add_account('CAD income', account_type=INCOME, currency=CAD)
        self.add_account('USD asset', currency=USD)
        self.add_entry('1/1/2008', 'USD entry', transfer='USD income', increase='1')
        self.add_account('CAD asset', currency=CAD)
        self.add_entry('1/1/2008', 'CAD entry', transfer='CAD income', increase='1')
        self.mainwindow.select_balance_sheet()
    
    def test_balance_pie_chart(self):
        # the amounts are converted to the default currency before being weighted
        expected = [
            ('CAD asset 55.6%', 1),
            ('USD asset 44.4%', 0.8),
        ]
        self.assertEqual(self.apie.data, expected)
    
    def test_cash_flow_pie_chart(self):
        # the amounts are converted to the default currency before being weighted
        self.mainwindow.select_income_statement()
        expected = [
            ('CAD income 55.6%', 1),
            ('USD income 44.4%', 0.8),
        ]
        self.assertEqual(self.ipie.data, expected)
    

class NegativeAssetValue(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('foo')
        self.add_account('bar')
        self.add_entry(date='01/08/2008', transfer='foo', increase='1')
        self.mainwindow.select_balance_sheet()
    
    def test_balance_pie_chart(self):
        # negative balances are ignored
        self.assertEqual(self.apie.data, [('bar 100.0%', 1)])
    

class AccountGroup(TestCase):
    def setUp(self):
        self.create_instances()
        self.bsheet.add_account_group()
        self.bsheet.selected.name = 'group'
        self.bsheet.save_edits()
        self.bsheet.add_account() # the group is now expanded
        self.bsheet.selected.name = 'foo'
        self.bsheet.save_edits()
        self.bsheet.show_selected_account()
        self.add_entry(increase='1')
        self.add_account('bar', group_name='group')
        self.add_entry(increase='2')
        self.add_account('baz')
        self.add_entry(increase='7')
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
    
    def test_collapse_group(self):
        # when we collapse the group, 'foo' and 'bar' are grouped together
        self.bsheet.collapse_node(self.bsheet.assets[0])
        # we must not refresh the bsheet. group collapsing is called in the middle of an outline
        # view event, refreshing the outline during that call causes a crash
        self.check_gui_calls(self.bsheet_gui)
        expected = [
            ('baz 70.0%', 7),
            ('group 30.0%', 3),
        ]
        self.assertEqual(self.apie.data, expected)
    
    def test_expand_group(self):
        # when we expand the group again, 'foo' and 'bar' go back to separate
        self.bsheet.expand_node(self.bsheet.assets[0])
        self.check_gui_calls(self.bsheet_gui) # see test_collapse_group
        expected = [
            ('baz 70.0%', 7),
            ('bar 20.0%', 2),
            ('foo 10.0%', 1),
        ]
        self.assertEqual(self.apie.data, expected)
    
    def test_pie_chart_data(self):
        # when the group is expanded, show all accounts individually
        expected = [
            ('baz 70.0%', 7),
            ('bar 20.0%', 2),
            ('foo 10.0%', 1),
        ]
        self.assertEqual(self.apie.data, expected)
    
