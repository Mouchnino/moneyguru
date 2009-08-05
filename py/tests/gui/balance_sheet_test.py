# coding: utf-8
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from datetime import date

from hsutil.currency import Currency, USD, CAD

from ..base import DocumentGUI, TestCase, TestSaveLoadMixin, CallLogger, CommonSetup
from ...app import Application
from ...document import Document
from ...gui.balance_sheet import BalanceSheet
from ...model import currency
from ...model.account import LIABILITY, INCOME, EXPENSE
from ...model.amount import Amount
from ...model.date import MonthRange

# IMPORTANT NOTE: Keep in mind that every node count check in these tests take the total node and the
# blank node into account. For example, the node acount of an empty ASSETS node is 2.

class _AccountsAndEntries(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account('income', account_type=INCOME)
        self.add_account('expense', account_type=EXPENSE)
        self.add_account('Account 1')
        self.add_entry('10/01/2008', 'Entry 1', transfer='income', increase='100.00')
        self.add_entry('13/01/2008', 'Entry 2', transfer='income', increase='150.00')
        self.add_account('Account 2')
        self.add_entry('11/12/2007', 'Entry 3', transfer='income', increase='100.00')
        self.add_entry('12/01/2008', 'Entry 4', transfer='expense', decrease='20.00')
        self.document.select_balance_sheet()
        self.clear_gui_calls()
    

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.check_gui_calls(self.bsheet_gui, refresh=1)
    
    def test_add_account(self):
        """The default name for an account is 'New Account', and the selection goes from None to 0.
        Then, on subsequent calls, a number is added next to 'New Account'
        """
        self.bsheet.add_account()
        self.assertEqual(self.account_names(), ['New account'])
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[0])
        self.bsheet.add_account()
        self.assertEqual(self.account_names(), ['New account', 'New account 1'])
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[1])
        self.bsheet.add_account()
        self.assertEqual(self.account_names(), ['New account', 'New account 1', 'New account 2'])
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[2])
    
    def test_add_account_in_other_groups(self):
        """When groups other than Assets are selected, new accounts go underneath it."""
        self.bsheet.selected = self.bsheet.liabilities
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.selected, self.bsheet.liabilities[0])
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.selected, self.bsheet.liabilities[1])
        self.bsheet.selected = self.bsheet.assets
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[0])
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[1])
        self.bsheet.selected = None
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[2])
    
    def test_add_account_with_total_node_selected(self):
        # The added account will be of the type of the type node we're under
        self.bsheet.selected = self.bsheet.liabilities[0] # total node
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.liabilities[0].name, 'New account')
    
    def test_add_group(self):
        """add_group() creates a new account group in the selected base group"""
        self.bsheet.selected = self.bsheet.liabilities
        self.bsheet.add_account_group()
        self.assertEqual(self.bsheet.selected, self.bsheet.liabilities[0])
        self.assertEqual(self.bsheet.liabilities[0].name, 'New group')
        self.assertTrue(self.bsheet.liabilities[0].is_group)
        self.assertTrue(self.document.is_dirty())
    
    def test_add_group(self):
        """Adding a group refreshes the view and goes into edit mode."""
        self.bsheet.add_account_group()
        self.check_gui_calls(self.bsheet_gui, stop_editing=1, start_editing=1, refresh=1, update_selection=1)
    
    def test_add_group_with_total_node_selected(self):
        # The added group will be of the type of the type node we're under
        self.bsheet.selected = self.bsheet.liabilities[0] # total node
        self.bsheet.add_account_group()
        self.assertEqual(self.bsheet.liabilities[0].name, 'New group')
    
    def test_balance_sheet(self):
        """The balance sheet is empty... well, except for the "total" and blank nodes."""
        self.assertEqual([x.name for x in self.bsheet], ['ASSETS',  'LIABILITIES',  'NET WORTH'])
        self.assertEqual(len(self.bsheet.assets), 2)
        self.assertEqual(len(self.bsheet.liabilities), 2)
    
    def test_is_excluded_is_bool_for_empty_groups_and_type(self):
        # previously, empty lists would be returned, causing a crash in the gui
        self.assertTrue(isinstance(self.bsheet.assets.is_excluded, bool))
        self.bsheet.add_account_group()
        self.assertTrue(isinstance(self.bsheet.assets[0].is_excluded, bool))
    

class AccountHierarchy(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Asset 1')
        self.add_group('Bank')
        self.add_account('Bank 1', group_name='Bank')
        self.add_account('Liability 1', account_type=LIABILITY)
        self.add_group('Loans', account_type=LIABILITY)
        self.add_account('Loan 1', account_type=LIABILITY, group_name='Loans')
        self.document.select_balance_sheet()
        self.clear_gui_calls()

    def test_balance_sheet(self):
        """The balance sheet shows the hierarchy correctly."""
        self.assertEqual(self.bsheet.assets[0].name, 'Bank')
        self.assertEqual(self.bsheet.assets[0][0].name, 'Bank 1')
        self.assertEqual(self.bsheet.assets[0][1].name, 'Total Bank')
        self.assertEqual(self.bsheet.assets[0][2].name, None)
        self.assertEqual(self.bsheet.assets[1].name, 'Asset 1')
        self.assertEqual(self.bsheet.assets[2].name, 'TOTAL ASSETS')
        self.assertEqual(self.bsheet.assets[3].name, None)
        self.assertEqual(self.bsheet.liabilities[0].name, 'Loans')
        self.assertEqual(self.bsheet.liabilities[0][0].name, 'Loan 1')
        self.assertEqual(self.bsheet.liabilities[1].name, 'Liability 1')
    
    def test_can_show_selected_account(self):
        # Is the selected item is not an account, can_show_selected_account returns False
        self.bsheet.selected = self.bsheet.assets
        self.assertFalse(self.bsheet.can_show_selected_account)
        self.bsheet.selected = self.bsheet.assets[0] # the group
        self.assertFalse(self.bsheet.can_show_selected_account)
        self.bsheet.selected = self.bsheet.assets[0][0]
        self.assertTrue(self.bsheet.can_show_selected_account)
    
    def test_cancel_edits(self):
        """cancel_edits() reverts the node name to the old value"""
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.selected.name = 'foobar'
        self.bsheet.cancel_edits()
        self.assertEqual(self.bsheet.selected.name, 'Asset 1')
    
    def test_delete_account(self):
        """Removing an account refreshes the view."""
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.delete()
        self.check_gui_calls(self.bsheet_gui, refresh=1)
    
    def test_save_edits(self):
        """save_edits() refreshes the view"""
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.selected.name = 'foobar'
        self.bsheet.save_edits()
        self.check_gui_calls(self.bsheet_gui, refresh=1)
    
    def test_show_selected_account(self):
        """show_selected_account() switches to the account view."""
        self.bsheet.selected = self.bsheet.assets[0][0]
        self.clear_gui_calls()
        self.bsheet.show_selected_account()
        # no show_line_graph because it was already selected in the etable view before
        self.check_gui_calls(self.mainwindow_gui, show_entry_table=1)
        self.assertEqual(self.document.selected_account.name, 'Bank 1')
    

class OneEmptyAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.document.select_balance_sheet()
        self.clear_gui_calls()
    
    def test_add_accounts_after_current(self):
        """The selection follows the newly added account"""
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[1])
        self.check_gui_calls(self.bsheet_gui, update_selection=1, start_editing=1, stop_editing=1, refresh=1)
    
    def test_duplicate_account_name(self):
        # when the user enters a duplicate account name, show a dialog.
        self.bsheet.add_account()
        self.bsheet.selected.name = 'checking' # fails
        self.bsheet.save_edits()
        self.assertEqual(self.bsheet.selected.name, 'New account')
        self.check_gui_calls_partial(self.bsheet_gui, show_message=1)
    
    def test_make_account_liability(self):
        """Making the account a liability account refreshes all views."""
        self.bsheet.move(self.bsheet.get_path(self.bsheet.assets[0]), self.bsheet.get_path(self.bsheet.liabilities))
        self.check_gui_calls(self.nwgraph_gui, refresh=1)
    

class OneAccountInEditionMode(TestCase):
    def setUp(self):
        self.create_instances()
        self.bsheet.add_account()
        self.bsheet.selected.name = 'foo'
    
    def test_add_account(self):
        # What is in the edition buffer is saved before a new account is created
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.assets[0].name, 'foo')
        # The new account name was determined after the save
        self.assertEqual(self.bsheet.assets[1].name, 'New account')
    
    def test_add_group(self):
        # What is in the edition buffer is saved before a new group is created
        self.bsheet.add_account_group()
        self.assertEqual(self.bsheet.assets[1].name, 'foo')
    

class OnlyOneGroup(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group('Group')
        self.clear_gui_calls()
    
    def test_accounts_sorted(self):
        """Accounts inside a group are sorted alphabetically."""
        self.add_account('Zorg', group_name='Group', select=False)
        self.add_account('Albany', group_name='Group', select=False)
        self.add_account(u'Réal', group_name='Group', select=False)
        self.add_account('Rex', group_name='Group', select=False)
        self.assertEqual([x.name for x in self.bsheet.assets[0][:4]], ['Albany', u'Réal', 'Rex', 'Zorg'])
    
    def test_balance_sheet(self):
        self.assertEqual(self.bsheet.assets[0].name, 'Group')
    
    def test_save_edits_on_group(self):
        """save_edits() on a group refreshes the view too"""
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.selected.name = 'foobar'
        self.bsheet.save_edits()
        self.check_gui_calls(self.bsheet_gui, refresh=1)
    
    
class OneGroupInEditionMode(TestCase):
    def setUp(self):
        self.create_instances()
        self.bsheet.add_account_group()
        self.bsheet.selected.name = 'foo'
    
    def test_add_account(self):
        # What is in the edition buffer is saved before a new account is created
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.assets[0].name, 'foo')
    

class OneAccountAndOneGroup(TestCase, TestSaveLoadMixin):
    # TestSaveLoadMixin is to make sure that empty groups are kept when saving/loading
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_group()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # the group
    
    def test_add_account(self):
        """New accounts are created under the selected user created group"""
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.assets.children_count, 4)
        self.assertEqual(self.bsheet.assets[0].children_count, 3)
    

class OneAccountInOneGroup(TestCase, TestSaveLoadMixin):
    # TestSaveLoadMixin is to make sure that groups are saved
    def setUp(self):
        self.create_instances()
        self.add_group('group')
        self.add_account(group_name='group')
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0][0] # the account in the group
    
    def test_add_account(self):
        """Adding an account when the selection is an account under a user created group creates
        the new account under that same group
        """
        self.bsheet.add_account()
        self.assertEqual(self.bsheet.assets[0].children_count, 4)
    

class AccountsAndEntries(_AccountsAndEntries):
    def test_balance_sheet(self):
        self.assertEqual(self.document.date_range, MonthRange(date(2008, 1, 1)))
        self.assertEqual(self.bsheet.assets[0].name, 'Account 1')
        self.assertEqual(self.bsheet.assets[0].start, '0.00')
        self.assertEqual(self.bsheet.assets[0].delta, '250.00')
        self.assertEqual(self.bsheet.assets[0].delta_perc, '---')
        self.assertEqual(self.bsheet.assets[0].end, '250.00')
        self.assertEqual(self.bsheet.assets[1].name, 'Account 2')
        self.assertEqual(self.bsheet.assets[1].start, '100.00')
        self.assertEqual(self.bsheet.assets[1].delta, '-20.00')
        self.assertEqual(self.bsheet.assets[1].delta_perc, '-20.0%')
        self.assertEqual(self.bsheet.assets[1].end, '80.00')
        self.assertEqual(self.bsheet.assets.start, '100.00')
        self.assertEqual(self.bsheet.assets.delta, '230.00')
        self.assertEqual(self.bsheet.assets.delta_perc, '+230.0%')
        self.assertEqual(self.bsheet.assets.end, '330.00')
        self.assertEqual(self.bsheet.net_worth.start, '100.00')
        self.assertEqual(self.bsheet.net_worth.delta, '230.00')
        self.assertEqual(self.bsheet.net_worth.delta_perc, '+230.0%')
        self.assertEqual(self.bsheet.net_worth.end, '330.00')
    
    def test_budget(self):
        # Account 1 is the target of the expense budget, and Account 2 is the target of the income
        # Assign budgeted amounts to the appropriate accounts.
        self.mock_today(2008, 1, 15)
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.set_budget('400', 1) # + 150
        self.istatement.selected = self.istatement.expenses[0]
        self.set_budget('100', 0) # + 80
        self.document.select_balance_sheet()
        self.assertEqual(self.bsheet.assets[0].end, '170.00') # 250 - 80
        self.assertEqual(self.bsheet.assets[1].end, '230.00') # 80 + 150
        self.assertEqual(self.bsheet.assets.end, '400.00')
        # now, is we go to the next date range, the "start" value must be the same
        self.document.select_next_date_range()
        self.assertEqual(self.bsheet.assets[0].start, '170.00') # 250 - 80
        self.assertEqual(self.bsheet.assets[1].start, '230.00') # 80 + 150
        self.assertEqual(self.bsheet.assets.start, '400.00')
        # when calculating prev budgeting, calculate it for *everything* previous, not just the previous slice!
        self.document.select_next_date_range()
        self.assertEqual(self.bsheet.assets[0].start, '70.00') # 250 - 80
        self.assertEqual(self.bsheet.assets[1].start, '630.00') # 80 + 150
        self.assertEqual(self.bsheet.assets.start, '700.00')
    
    def test_budget_multiple_currencies(self):
        # budgeted amounts must be correctly converted to the target's currency
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        self.mock_today(2008, 1, 15)
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.apanel.load()
        self.apanel.currency_index = Currency.all.index(CAD)
        self.apanel.budget = '400' # + 150
        self.apanel.budget_target_index = 0
        self.apanel.save()
        self.document.select_balance_sheet()
        self.assertEqual(self.bsheet.assets[0].end, '500.00')
    
    def test_budget_target_liability(self):
        # The budgeted amount must be normalized before being added to a liability amount
        self.mock_today(2008, 1, 15)
        self.add_account('foo', account_type=LIABILITY)
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.set_budget('400', 2) # + 150
        self.document.select_balance_sheet()
        self.assertEqual(self.bsheet.liabilities[0].end, '-150.00')
    
    def test_change_date_range(self):
        self.document.date_range = self.document.date_range.prev()
        self.assertEqual(self.bsheet.assets[0].end, '0.00')
        self.assertEqual(self.bsheet.assets[1].start, '0.00')
        self.assertEqual(self.bsheet.assets[1].end, '100.00')
    
    def test_exclude_total_node(self):
        # excluding a total node does nothing (no crash)
        self.bsheet.selected = self.bsheet.assets[2] # total node
        self.bsheet.toggle_excluded()
        self.assertFalse(self.bsheet.assets[2].is_excluded)
    
    def test_exclude_type(self):
        # Excluding a type toggles exclusion for all accounts of that type
        self.bsheet.selected = self.bsheet.assets
        self.bsheet.toggle_excluded()
        self.assertEqual(self.bsheet.assets.children_count, 3) # the 2 accounts and the blank node
        self.assertTrue(self.bsheet.assets[2].is_blank)
        self.assertEqual(self.bsheet.assets[0].start, '')
        self.assertEqual(self.bsheet.assets[0].end, '')
        self.assertEqual(self.bsheet.assets[0].delta, '')
        self.assertEqual(self.bsheet.assets[0].delta_perc, '')
        self.assertEqual(self.bsheet.assets[1].start, '')
        self.assertEqual(self.bsheet.assets[1].end, '')
        self.assertEqual(self.bsheet.assets[1].delta, '')
        self.assertEqual(self.bsheet.assets[1].delta_perc, '')
        self.assertTrue(self.bsheet.assets.is_excluded)
    
    def test_show_account_and_come_back(self):
        # When going back to a report, the selected account in the document is also selected in the
        # report.
        self.bsheet.selected = self.bsheet.assets[1] # Account 2
        self.bsheet.show_selected_account()
        self.mainwindow.navigate_back()
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[1])
    
    def test_shown_account_is_sticky(self):
        # When calling show_selected_account, soming back in a report and selecting another account
        # does not change the account that will be shown is select_entry_table is called.
        self.bsheet.selected = self.bsheet.assets[0] # Account 1
        self.bsheet.show_selected_account()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # Account 2
        self.document.select_entry_table()
        self.assertEqual(self.balgraph.title, 'Account 1')
        self.assertEqual(self.etable[0].description, 'Entry 1')
    

class MultipleCurrencies(TestCase):
    def setUp(self):
        self.app = Application(CallLogger(), default_currency=CAD)
        self.create_instances()
        self.document.select_month_range()
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        USD.set_CAD_value(0.9, date(2008, 1, 31))
        self.add_group('Group')
        self.add_account('USD account', currency=USD, group_name='Group')
        self.add_entry('1/1/2007', 'USD entry', increase='50.00')
        self.add_entry('1/1/2008', 'USD entry', increase='80.00')
        self.add_entry('31/1/2008', 'USD entry', increase='20.00')
        self.assertEqual(self.document.selected_account.balance(), Amount(150, USD))
        self.add_account('CAD account', currency=CAD, group_name='Group')
        self.add_entry('1/1/2008', 'USD entry', increase='100.00')
        self.document.select_balance_sheet()

    def test_balance_sheet(self):
        self.assertEqual(USD.value_in(CAD, date(2008, 2, 1)), 0.9)
        self.assertEqual(self.document.date_range, MonthRange(date(2008, 1, 1)))
        self.assertEqual(self.bsheet.assets.start, '40.00')
        self.assertEqual(self.bsheet.assets.end, '235.00')
        self.assertEqual(self.bsheet.assets.delta, '195.00')
        self.assertEqual(self.bsheet.assets.delta_perc, '+487.5%')
        self.assertEqual(self.bsheet.assets[0].start, '40.00')
        self.assertEqual(self.bsheet.assets[0].end, '235.00')
        self.assertEqual(self.bsheet.assets[0].delta, '195.00')
        self.assertEqual(self.bsheet.assets[0].delta_perc, '+487.5%')
    
    def test_delete_transaction(self):
        # Deleting a transaction correctly updates the balance sheet balances. Previously, the
        # cache in Account would not correctly be cleared on cook()
        self.document.select_transaction_table()
        self.ttable.select([3]) # last entry, on the 31st
        self.ttable.delete()
        self.document.select_balance_sheet()
        self.assertEqual(self.bsheet.assets.end, '217.00')
    
    def test_exclude_group(self):
        # Excluding a group excludes all sub-accounts and removes the total node
        self.bsheet.selected = self.bsheet.assets[0] # Group
        self.bsheet.toggle_excluded()
        self.assertEqual(self.bsheet.assets[0].children_count, 3) # the 2 accounts and the blank node
        self.assertTrue(self.bsheet.assets[0][2].is_blank)
        self.assertEqual(self.bsheet.assets[0][0].start, '')
        self.assertEqual(self.bsheet.assets[0][0].end, '')
        self.assertEqual(self.bsheet.assets[0][0].delta, '')
        self.assertEqual(self.bsheet.assets[0][0].delta_perc, '')
        self.assertEqual(self.bsheet.assets[0][1].start, '')
        self.assertEqual(self.bsheet.assets[0][1].end, '')
        self.assertEqual(self.bsheet.assets[0][1].delta, '')
        self.assertEqual(self.bsheet.assets[0][1].delta_perc, '')
        self.assertTrue(self.bsheet.assets[0].is_excluded)
    
    def test_exclude_group_with_one_child_excluded(self):
        # as soon as one child is excluded, the toggle_excluded action re-includes all children
        self.bsheet.selected = self.bsheet.assets[0][1]
        self.bsheet.toggle_excluded()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.toggle_excluded() # excludes all
        self.assertTrue(self.bsheet.assets[0].is_excluded)
        self.assertTrue(self.bsheet.assets[0][0].is_excluded)
        self.assertTrue(self.bsheet.assets[0][1].is_excluded)
        self.bsheet.toggle_excluded() # re-includes all
        self.assertFalse(self.bsheet.assets[0].is_excluded)
        self.assertEqual(self.bsheet.assets[0].children_count, 4) # all there
        self.assertFalse(self.bsheet.assets[0][0].is_excluded)
        self.assertFalse(self.bsheet.assets[0][1].is_excluded)
    

class Liability(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group('foo', account_type=LIABILITY)
        self.add_account('Credit card', account_type=LIABILITY, group_name='foo')
        self.add_entry(date='31/12/2007', description='Starting balance', decrease='100.00')
        self.add_entry(date='1/1/2008', description='Expensive jewel', increase='1200.00')
        self.document.select_balance_sheet()

    def test_balance_sheet(self):
        """Liability amounts are shown in their normal form (credit is positive)"""
        self.assertEqual(self.bsheet.liabilities[0][0].name, 'Credit card')
        self.assertEqual(self.bsheet.liabilities[0][0].start, '-100.00')
        self.assertEqual(self.bsheet.liabilities[0][0].end, '1100.00')
        self.assertEqual(self.bsheet.liabilities[0].start, '-100.00')
        self.assertEqual(self.bsheet.liabilities[0].end, '1100.00')
        self.assertEqual(self.bsheet.liabilities.start, '-100.00')
        self.assertEqual(self.bsheet.liabilities.end, '1100.00')
        self.assertEqual(self.bsheet.net_worth.start, '100.00')
        self.assertEqual(self.bsheet.net_worth.end, '-1100.00')
        self.assertEqual(self.bsheet.net_worth.delta, '-1200.00')
    

class LoadFileBeforeCreatingInstances(TestCase):
    def setUp(self):
        self.app = Application(CallLogger())
        self.document = Document(DocumentGUI(), self.app)
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.document.load_from_xml(self.filepath('xml/moneyguru.xml'))
        self.create_instances()
    
    def test_refresh_on_connect(self):
        """the account tree refreshes itself and selects the first asset"""
        self.assertEqual(self.bsheet.assets.children_count, 4)
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[0])
        self.check_gui_calls(self.bsheet_gui, refresh=1)
    

class TwoAccountsInTwoReports(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('asset')
        self.add_account('income', account_type=INCOME)
    
    def test_show_account_then_select_other_report(self):
        # If the shown account is not in the shown report, select the first account
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.document.select_balance_sheet()
        self.assertEqual(self.bsheet.selected, self.bsheet.assets[0])
    

class NegativeNetworthStart(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Loan', account_type=LIABILITY)
        self.add_entry(date='31/12/2007', description='Starting balance', increase='1000')
        self.add_account('Checking')
        self.add_entry(date='1/1/2008', description='Salary', increase='1500.00')
        self.document.select_balance_sheet()
    
    def test_delta_perc(self):
        # When the balance at the start is negative, don't display a delta %
        self.assertEqual(self.bsheet.net_worth.delta_perc, '---')
    

class OneExcludedAccount(_AccountsAndEntries):
    def setUp(self):
        _AccountsAndEntries.setUp(self)
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.toggle_excluded()
    
    def test_gui_calls(self):
        # account exclusion refreshes the sheet
        self.check_gui_calls(self.bsheet_gui, refresh=1)
    
    def test_save_and_load(self):
        # account exclusion is persistent
        newdoc = self.save_and_load(newapp=False)
        bsheet = BalanceSheet(CallLogger(), newdoc)
        bsheet.connect()
        self.assertTrue(bsheet.assets[1].is_excluded)
    
    def test_values(self):
        # Excluding an account removes its amount from the totals and blanks its own amounts
        self.assertEqual(self.bsheet.assets[1].start, '')
        self.assertEqual(self.bsheet.assets[1].end, '')
        self.assertEqual(self.bsheet.assets[1].delta, '')
        self.assertEqual(self.bsheet.assets[1].delta_perc, '')
        self.assertEqual(self.bsheet.assets.start, '0.00')
        self.assertEqual(self.bsheet.assets.end, '250.00')
        self.assertEqual(self.bsheet.assets.delta, '250.00')
        self.assertEqual(self.bsheet.assets.delta_perc, '---')
        self.assertTrue(self.bsheet.assets[1].is_excluded)
    
