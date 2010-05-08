# -*- coding: utf-8 -*-
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from datetime import date

from nose.tools import eq_

from hsutil.currency import Currency, USD, CAD
from hsutil.testutil import Patcher

from ..base import DocumentGUI, TestCase, TestSaveLoadMixin, ApplicationGUI, TestApp, with_app
from ...app import Application
from ...const import PaneType
from ...document import Document
from ...model.account import AccountType
from ...model.amount import Amount
from ...model.date import MonthRange

# IMPORTANT NOTE: Keep in mind that every node count check in these tests take the total node and the
# blank node into account. For example, the node acount of an empty ASSETS node is 2.

class _AccountsAndEntries(TestCase):
    def setUp(self):
        self.create_instances()
        self.drsel.select_month_range()
        self.add_account('income', account_type=AccountType.Income)
        self.add_account('expense', account_type=AccountType.Expense)
        self.add_account('Account 1')
        self.mainwindow.show_account()
        self.add_entry('10/01/2008', 'Entry 1', transfer='income', increase='100.00')
        self.add_entry('13/01/2008', 'Entry 2', transfer='income', increase='150.00')
        self.add_account('Account 2')
        self.mainwindow.show_account()
        self.add_entry('11/12/2007', 'Entry 3', transfer='income', increase='100.00')
        self.add_entry('12/01/2008', 'Entry 4', transfer='expense', decrease='20.00')
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
    
#--- Pristine app
@with_app(TestApp)
def test_add_account(app):
    # The default name for an account is 'New Account', and the selection goes from None to 0.
    # Then, on subsequent calls, a number is added next to 'New Account'.
    app.bsheet.add_account()
    eq_(app.account_names(), ['New account'])
    eq_(app.bsheet.selected, app.bsheet.assets[0])
    app.bsheet.add_account()
    eq_(app.account_names(), ['New account', 'New account 1'])
    eq_(app.bsheet.selected, app.bsheet.assets[1])
    app.bsheet.add_account()
    eq_(app.account_names(), ['New account', 'New account 1', 'New account 2'])
    eq_(app.bsheet.selected, app.bsheet.assets[2])

@with_app(TestApp)
def test_add_account_in_other_groups(app):
    # When groups other than Assets are selected, new accounts go underneath it.
    app.bsheet.selected = app.bsheet.liabilities
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.liabilities[0])
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.liabilities[1])
    app.bsheet.selected = app.bsheet.assets
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[0])
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[1])
    app.bsheet.selected = None
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[2])

@with_app(TestApp)
def test_add_account_with_total_node_selected(app):
    # The added account will be of the type of the type node we're under
    app.bsheet.selected = app.bsheet.liabilities[0] # total node
    app.bsheet.add_account()
    eq_(app.bsheet.liabilities[0].name, 'New account')

@with_app(TestApp)
def test_add_group(app):
    # add_group() creates a new account group in the selected base group.
    app.bsheet.selected = app.bsheet.liabilities
    app.bsheet.add_account_group()
    eq_(app.bsheet.selected, app.bsheet.liabilities[0])
    eq_(app.bsheet.liabilities[0].name, 'New group')
    assert app.bsheet.liabilities[0].is_group
    assert app.doc.is_dirty()

@with_app(TestApp)
def test_add_group_with_total_node_selected(app):
    # The added group will be of the type of the type node we're under
    app.bsheet.selected = app.bsheet.liabilities[0] # total node
    app.bsheet.add_account_group()
    eq_(app.bsheet.liabilities[0].name, 'New group')

@with_app(TestApp)
def test_balance_sheet(app):
    # The balance sheet is empty
    eq_([x.name for x in app.bsheet], ['ASSETS',  'LIABILITIES',  'NET WORTH'])
    eq_(app.account_node_subaccount_count(app.bsheet.assets), 0)
    eq_(app.account_node_subaccount_count(app.bsheet.liabilities), 0)

@with_app(TestApp)
def test_can_delete(app):
    # can_delete doesn't crash when nothing is selected
    assert not app.bsheet.can_delete() # no crash

@with_app(TestApp)
def test_is_excluded_is_bool_for_empty_groups_and_type(app):
    # previously, empty lists would be returned, causing a crash in the gui
    assert isinstance(app.bsheet.assets.is_excluded, bool)
    app.bsheet.add_account_group()
    assert isinstance(app.bsheet.assets[0].is_excluded, bool)

@with_app(TestApp)
def test_root_nodes_initially_expanded(app):
    # When the preference doesn't say otherwise, root nodes are expanded.
    eq_(app.bsheet.expanded_paths, [(0, ), (1, )])

@with_app(TestApp)
def test_save_edits_doesnt_lead_to_infinite_loop(app):
    # in save_edits, self.edited must be put to None asap because changes in the document could
    # lead to refreshes in the views that would call save_edits again and create an infinite
    # loop
    app.bsheet.add_account()
    app.bsheet.assets[0].name = 'foo'
    def fake_refresh():
        assert app.bsheet.edited is None
    with Patcher() as p:
        p.patch(app.bsheet_gui, 'refresh', fake_refresh)
        app.bsheet.save_edits()

class AccountHierarchy(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Asset 1', account_number='4242')
        self.add_group('Bank')
        self.add_account('Bank 1', group_name='Bank')
        self.add_account('Liability 1', account_type=AccountType.Liability)
        self.add_group('Loans', account_type=AccountType.Liability)
        self.add_account('Loan 1', account_type=AccountType.Liability, group_name='Loans')
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
    
    def test_balance_sheet(self):
        # The balance sheet shows the hierarchy correctly.
        eq_(self.bsheet.assets.account_number, '') # all nodes have an account_number property
        eq_(self.bsheet.net_worth.account_number, '')
        eq_(self.bsheet.assets[0].name, 'Bank')
        eq_(self.bsheet.assets[0][0].name, 'Bank 1')
        eq_(self.bsheet.assets[0][1].name, 'Total Bank')
        eq_(self.bsheet.assets[0][2].name, None)
        eq_(self.bsheet.assets[1].name, 'Asset 1')
        eq_(self.bsheet.assets[1].account_number, '4242')
        eq_(self.bsheet.assets[2].name, 'TOTAL ASSETS')
        eq_(self.bsheet.assets[3].name, None)
        eq_(self.bsheet.liabilities[0].name, 'Loans')
        eq_(self.bsheet.liabilities[0][0].name, 'Loan 1')
        eq_(self.bsheet.liabilities[1].name, 'Liability 1')
    
    def test_can_show_selected_account(self):
        # Is the selected item is not an account, can_show_selected_account returns False
        self.bsheet.selected = self.bsheet.assets
        assert not self.bsheet.can_show_selected_account
        self.bsheet.selected = self.bsheet.assets[0] # the group
        assert not self.bsheet.can_show_selected_account
        self.bsheet.selected = self.bsheet.assets[0][0]
        assert self.bsheet.can_show_selected_account
    
    def test_cancel_edits(self):
        # cancel_edits() reverts the node name to the old value.
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.selected.name = 'foobar'
        self.bsheet.cancel_edits()
        eq_(self.bsheet.selected.name, 'Asset 1')
    
    def test_delete_account(self):
        # Removing an account refreshes the view and stops any edition that was going on (if edition
        # is not stopped, the current buffer will be applied to the node under the deleted account)
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.delete()
        self.check_gui_calls(self.bsheet_gui, ['refresh', 'stop_editing'])
    
    def test_is_subtotal(self):
        # Node.is_subtotal is True when the node under it is a total node (is_total).
        assert not self.bsheet.assets.is_subtotal
        assert not self.bsheet.assets[0].is_subtotal
        assert self.bsheet.assets[0][0].is_subtotal
        assert not self.bsheet.assets[0][1].is_subtotal
        assert not self.bsheet.assets[0][2].is_subtotal
        assert not self.bsheet.liabilities.is_subtotal
    
    def test_save_edits(self):
        # save_edits() refreshes the view.
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.selected.name = 'foobar'
        self.bsheet.save_edits()
        self.check_gui_calls(self.bsheet_gui, ['refresh'])
    
    def test_show_selected_account(self):
        # show_selected_account() switches to the account view.
        self.bsheet.selected = self.bsheet.assets[0][0]
        self.clear_gui_calls()
        self.bsheet.show_selected_account()
        # no show_line_graph because it was already selected in the etable view before
        self.ta.check_current_pane(PaneType.Account, account_name='Bank 1')
    

#--- One account
def app_one_account():
    app = TestApp()
    app.add_account('Checking')
    app.clear_gui_calls()
    return app

@with_app(app_one_account)
def test_add_accounts_after_current(app):
    # The selection follows the newly added account.
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[1])
    app.check_gui_calls(app.bsheet_gui, ['update_selection', 'start_editing', 'stop_editing', 'refresh'])

@with_app(app_one_account)
def test_duplicate_account_name(app):
    # when the user enters a duplicate account name, show a dialog.
    app.bsheet.add_account()
    app.bsheet.selected.name = 'checking' # fails
    app.bsheet.save_edits()
    eq_(app.bsheet.selected.name, 'New account')
    app.check_gui_calls_partial(app.mainwindow_gui, ['show_message'])
    assert app.bsheet.edited is None

@with_app(app_one_account)
def test_make_account_liability(app):
    # Making the account a liability account refreshes all views.
    app.bsheet.move(app.bsheet.get_path(app.bsheet.assets[0]), app.bsheet.get_path(app.bsheet.liabilities))
    app.check_gui_calls(app.nwgraph_gui, ['refresh'])

@with_app(app_one_account)
def test_selection_follows_account_after_editing(app):
    # After editing, selection follows the account that was edited. This is important to avoid
    # confusion when invoking the account panel when still editing the name.
    app.mw.new_item() # 'New Account', so it's after 'Checking'
    app.bsheet.selected.name = 'aaa' # will end up *before* 'Checking'
    app.mw.edit_item()
    eq_(app.bsheet.selected.name, 'aaa')

class OneAccountInEditionMode(TestCase):
    def setUp(self):
        self.create_instances()
        self.bsheet.add_account()
        self.bsheet.selected.name = 'foo'
    
    def test_add_account(self):
        # What is in the edition buffer is saved before a new account is created
        self.bsheet.add_account()
        eq_(self.bsheet.assets[0].name, 'foo')
        # The new account name was determined after the save
        eq_(self.bsheet.assets[1].name, 'New account')
    
    def test_add_group(self):
        # What is in the edition buffer is saved before a new group is created
        self.bsheet.add_account_group()
        eq_(self.bsheet.assets[1].name, 'foo')
    

class OnlyOneGroup(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group('Group')
        self.clear_gui_calls()
    
    def test_accounts_sorted(self):
        # Accounts inside a group are sorted alphabetically.
        self.add_account('Zorg', group_name='Group')
        self.add_account('Albany', group_name='Group')
        self.add_account(u'Réal', group_name='Group')
        self.add_account('Rex', group_name='Group')
        eq_([x.name for x in self.bsheet.assets[0][:4]], ['Albany', u'Réal', 'Rex', 'Zorg'])
    
    def test_balance_sheet(self):
        eq_(self.bsheet.assets[0].name, 'Group')
    
    def test_save_edits_on_group(self):
        # save_edits() on a group refreshes the view too.
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.selected.name = 'foobar'
        self.bsheet.save_edits()
        self.check_gui_calls(self.bsheet_gui, ['refresh'])
    

class OneGroupInEditionMode(TestCase):
    def setUp(self):
        self.create_instances()
        self.bsheet.add_account_group()
        self.bsheet.selected.name = 'foo'
    
    def test_add_account(self):
        # What is in the edition buffer is saved before a new account is created
        self.bsheet.add_account()
        eq_(self.bsheet.assets[0].name, 'foo')
    

class OneAccountAndOneGroup(TestCase, TestSaveLoadMixin):
    # TestSaveLoadMixin is to make sure that empty groups are kept when saving/loading
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_group()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # the group
    
    def test_add_account(self):
        # New accounts are created under the selected user created group.
        self.bsheet.add_account()
        eq_(self.account_node_subaccount_count(self.bsheet.assets), 2)
        eq_(self.account_node_subaccount_count(self.bsheet.assets[0]), 1)
    

#--- Account in group
def app_account_in_group():
    app = TestApp()
    app.add_group('group')
    app.add_account(group_name='group')
    app.bsheet.selected = app.bsheet.assets[0][0] # the account in the group
    return app

@with_app(app_account_in_group)
def test_add_account_with_group_selected(app):
    # Adding an account when the selection is an account under a user created group creates
    # the new account under that same group.
    app.bsheet.add_account()
    eq_(app.account_node_subaccount_count(app.bsheet.assets[0]), 2)

@with_app(app_account_in_group)
def test_expanded_nodes(app):
    # the `expanded_paths` property returns nodes that are... exapnded!
    app.bsheet.expand_node(app.bsheet.assets[0])
    eq_(app.bsheet.expanded_paths, [(0, ), (1, ), (0, 0)])

@with_app(app_account_in_group)
def test_is_subtotal(app):
    # In case we only have a group node just before a total node, this not will be considered
    # a subtotal node *only* if it's collapsed (if it's expanded, it has a total node hierarchy
    # of its own).
    app.bsheet.expand_node(app.bsheet.assets[0])
    assert not app.bsheet.assets[0].is_subtotal
    app.bsheet.collapse_node(app.bsheet.assets[0])
    assert app.bsheet.assets[0].is_subtotal

class AccountsAndEntries(_AccountsAndEntries):
    def test_balance_sheet(self):
        eq_(self.document.date_range, MonthRange(date(2008, 1, 1)))
        eq_(self.bsheet.assets[0].name, 'Account 1')
        eq_(self.bsheet.assets[0].start, '0.00')
        eq_(self.bsheet.assets[0].delta, '250.00')
        eq_(self.bsheet.assets[0].delta_perc, '---')
        eq_(self.bsheet.assets[0].end, '250.00')
        eq_(self.bsheet.assets[1].name, 'Account 2')
        eq_(self.bsheet.assets[1].start, '100.00')
        eq_(self.bsheet.assets[1].delta, '-20.00')
        eq_(self.bsheet.assets[1].delta_perc, '-20.0%')
        eq_(self.bsheet.assets[1].end, '80.00')
        eq_(self.bsheet.assets.start, '100.00')
        eq_(self.bsheet.assets.delta, '230.00')
        eq_(self.bsheet.assets.delta_perc, '+230.0%')
        eq_(self.bsheet.assets.end, '330.00')
        eq_(self.bsheet.net_worth.start, '100.00')
        eq_(self.bsheet.net_worth.delta, '230.00')
        eq_(self.bsheet.net_worth.delta_perc, '+230.0%')
        eq_(self.bsheet.net_worth.end, '330.00')
    
    def test_budget(self):
        # Account 1 is the target of the expense budget, and Account 2 is the target of the income
        # Assign budgeted amounts to the appropriate accounts.
        self.mock_today(2008, 1, 15)
        self.add_budget('income', 'Account 2', '400') # + 150
        self.add_budget('expense', 'Account 1', '100') # + 80
        self.mainwindow.select_balance_sheet()
        eq_(self.bsheet.assets[0].end, '250.00')
        eq_(self.bsheet.assets[0].budgeted, '-80.00')
        eq_(self.bsheet.assets[1].end, '80.00')
        eq_(self.bsheet.assets[1].budgeted, '150.00')
        eq_(self.bsheet.assets.end, '330.00')
        eq_(self.bsheet.assets.budgeted, '70.00')
        eq_(self.bsheet.net_worth.budgeted, '70.00')
        # When we go to the next date range, the "budgeted" value must be cumulated
        self.drsel.select_next_date_range()
        eq_(self.bsheet.assets[0].budgeted, '-180.00') # 80 + 100
        eq_(self.bsheet.assets[1].budgeted, '550.00') # 150 + 300
        eq_(self.bsheet.assets.budgeted, '370.00')
    
    def test_budget_multiple_currencies(self):
        # budgeted amounts must be correctly converted to the target's currency
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        self.mock_today(2008, 1, 15)
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.apanel.load()
        self.apanel.currency_index = Currency.all.index(CAD)
        self.apanel.save()
        self.add_budget('income', 'Account 1', '400 cad')
        self.mainwindow.select_balance_sheet()
        eq_(self.bsheet.assets[0].end, '250.00')
        eq_(self.bsheet.assets[0].budgeted, '250.00') # 400 / 2 / 0.8 = 250
    
    def test_budget_target_liability(self):
        # The budgeted amount must be normalized before being added to a liability amount
        self.mock_today(2008, 1, 15)
        self.add_account('foo', account_type=AccountType.Liability)
        self.add_budget('income', 'foo', '400')
        self.mainwindow.select_balance_sheet()
        eq_(self.bsheet.liabilities[0].end, '0.00')
        eq_(self.bsheet.liabilities[0].budgeted, '-150.00')
    
    def test_budget_without_target(self):
        # The Net Worth's "budgeted" column counts all budgets, including target-less ones
        self.mock_today(2008, 1, 15)
        self.add_budget('income', None, '400')
        self.mainwindow.select_balance_sheet()
        eq_(self.bsheet.net_worth.budgeted, '150.00')
    
    def test_change_date_range(self):
        self.document.date_range = self.document.date_range.prev()
        eq_(self.bsheet.assets[0].end, '0.00')
        eq_(self.bsheet.assets[1].start, '0.00')
        eq_(self.bsheet.assets[1].end, '100.00')
    
    def test_exclude_total_node(self):
        # excluding a total node does nothing (no crash)
        self.bsheet.selected = self.bsheet.assets[2] # total node
        self.bsheet.toggle_excluded()
        assert not self.bsheet.assets[2].is_excluded
    
    def test_exclude_type(self):
        # Excluding a type toggles exclusion for all accounts of that type
        self.bsheet.selected = self.bsheet.assets
        self.bsheet.toggle_excluded()
        # The total line for an excluded node diseappears, leaving only the 2 account lines and the
        # blank node
        eq_(self.bsheet.assets.children_count, 3)
        assert self.bsheet.assets[2].is_blank
        eq_(self.bsheet.assets[0].start, '')
        eq_(self.bsheet.assets[0].end, '')
        eq_(self.bsheet.assets[0].delta, '')
        eq_(self.bsheet.assets[0].delta_perc, '')
        eq_(self.bsheet.assets[1].start, '')
        eq_(self.bsheet.assets[1].end, '')
        eq_(self.bsheet.assets[1].delta, '')
        eq_(self.bsheet.assets[1].delta_perc, '')
        assert self.bsheet.assets.is_excluded
    
    def test_show_account_and_come_back(self):
        # When going back to a report, the selected account in the document is also selected in the
        # report.
        self.bsheet.selected = self.bsheet.assets[1] # Account 2
        self.bsheet.show_selected_account()
        self.mainwindow.navigate_back()
        eq_(self.bsheet.selected, self.bsheet.assets[1])
    
    def test_shown_account_is_sticky(self):
        # When calling show_selected_account, soming back in a report and selecting another account
        # does not change the account that will be shown is select_entry_table is called.
        self.bsheet.selected = self.bsheet.assets[0] # Account 1
        self.bsheet.show_selected_account()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # Account 2
        self.mainwindow.select_entry_table()
        eq_(self.balgraph.title, 'Account 1')
        eq_(self.etable[0].description, 'Entry 1')
    

class MultipleCurrencies(TestCase):
    def setUp(self):
        self.app = Application(ApplicationGUI(), default_currency=CAD)
        self.create_instances()
        self.drsel.select_month_range()
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        USD.set_CAD_value(0.9, date(2008, 1, 31))
        self.add_group('Group')
        self.add_account('USD account', currency=USD, group_name='Group')
        self.mainwindow.show_account()
        self.add_entry('1/1/2007', 'USD entry', increase='50.00')
        self.add_entry('1/1/2008', 'USD entry', increase='80.00')
        self.add_entry('31/1/2008', 'USD entry', increase='20.00')
        eq_(self.mainwindow.selected_account.balance(), Amount(150, USD))
        self.add_account('CAD account', currency=CAD, group_name='Group')
        self.mainwindow.show_account()
        self.add_entry('1/1/2008', 'USD entry', increase='100.00')
        self.mainwindow.select_balance_sheet()

    def test_balance_sheet(self):
        eq_(USD.value_in(CAD, date(2008, 2, 1)), 0.9)
        eq_(self.document.date_range, MonthRange(date(2008, 1, 1)))
        eq_(self.bsheet.assets.start, '40.00')
        eq_(self.bsheet.assets.end, '235.00')
        eq_(self.bsheet.assets.delta, '195.00')
        eq_(self.bsheet.assets.delta_perc, '+487.5%')
        eq_(self.bsheet.assets[0].start, '40.00')
        eq_(self.bsheet.assets[0].end, '235.00')
        eq_(self.bsheet.assets[0].delta, '195.00')
        eq_(self.bsheet.assets[0].delta_perc, '+487.5%')
    
    def test_delete_transaction(self):
        # Deleting a transaction correctly updates the balance sheet balances. Previously, the
        # cache in Account would not correctly be cleared on cook()
        self.mainwindow.select_transaction_table()
        self.ttable.select([2]) # last entry, on the 31st
        self.ttable.delete()
        self.mainwindow.select_balance_sheet()
        eq_(self.bsheet.assets.end, '217.00')
    
    def test_exclude_group(self):
        # Excluding a group excludes all sub-accounts and removes the total node
        self.bsheet.selected = self.bsheet.assets[0] # Group
        self.bsheet.toggle_excluded()
        eq_(self.bsheet.assets[0].children_count, 3) # the 2 accounts and the blank node
        assert self.bsheet.assets[0][2].is_blank
        eq_(self.bsheet.assets[0][0].start, '')
        eq_(self.bsheet.assets[0][0].end, '')
        eq_(self.bsheet.assets[0][0].delta, '')
        eq_(self.bsheet.assets[0][0].delta_perc, '')
        eq_(self.bsheet.assets[0][1].start, '')
        eq_(self.bsheet.assets[0][1].end, '')
        eq_(self.bsheet.assets[0][1].delta, '')
        eq_(self.bsheet.assets[0][1].delta_perc, '')
        assert self.bsheet.assets[0].is_excluded
    
    def test_exclude_group_with_one_child_excluded(self):
        # as soon as one child is excluded, the toggle_excluded action re-includes all children
        self.bsheet.selected = self.bsheet.assets[0][1]
        self.bsheet.toggle_excluded()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.toggle_excluded() # excludes all
        assert self.bsheet.assets[0].is_excluded
        assert self.bsheet.assets[0][0].is_excluded
        assert self.bsheet.assets[0][1].is_excluded
        self.bsheet.toggle_excluded() # re-includes all
        assert not self.bsheet.assets[0].is_excluded
        eq_(self.bsheet.assets[0].children_count, 4) # all there
        assert not self.bsheet.assets[0][0].is_excluded
        assert not self.bsheet.assets[0][1].is_excluded
    

class Liability(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group('foo', account_type=AccountType.Liability)
        self.add_account('Credit card', account_type=AccountType.Liability, group_name='foo')
        self.mainwindow.show_account()
        self.add_entry(date='31/12/2007', description='Starting balance', decrease='100.00')
        self.add_entry(date='1/1/2008', description='Expensive jewel', increase='1200.00')
        self.mainwindow.select_balance_sheet()
    
    def test_balance_sheet(self):
        # Liability amounts are shown in their normal form (credit is positive).
        eq_(self.bsheet.liabilities[0][0].name, 'Credit card')
        eq_(self.bsheet.liabilities[0][0].start, '-100.00')
        eq_(self.bsheet.liabilities[0][0].end, '1100.00')
        eq_(self.bsheet.liabilities[0].start, '-100.00')
        eq_(self.bsheet.liabilities[0].end, '1100.00')
        eq_(self.bsheet.liabilities.start, '-100.00')
        eq_(self.bsheet.liabilities.end, '1100.00')
        eq_(self.bsheet.net_worth.start, '100.00')
        eq_(self.bsheet.net_worth.end, '-1100.00')
        eq_(self.bsheet.net_worth.delta, '-1200.00')
    

class LoadFileBeforeCreatingInstances(TestCase):
    def setUp(self):
        self.app = Application(ApplicationGUI())
        self.document = Document(DocumentGUI(), self.app)
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.document.load_from_xml(self.filepath('moneyguru', 'simple.moneyguru'))
        self.create_instances()
    
    def test_refresh_on_connect(self):
        # the account tree refreshes itself and selects the first asset.
        eq_(self.account_node_subaccount_count(self.bsheet.assets), 2)
        eq_(self.bsheet.selected, self.bsheet.assets[0])
        self.check_gui_calls(self.bsheet_gui, ['refresh'])
    

class TwoAccountsInTwoReports(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('asset')
        self.add_account('income', account_type=AccountType.Income)
    
    def test_show_account_then_select_other_report(self):
        # If the shown account is not in the shown report, select the first account
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.mainwindow.select_balance_sheet()
        eq_(self.bsheet.selected, self.bsheet.assets[0])
    

class NegativeNetworthStart(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Loan', account_type=AccountType.Liability)
        self.mainwindow.show_account()
        self.add_entry(date='31/12/2007', description='Starting balance', increase='1000')
        self.add_account('Checking')
        self.mainwindow.show_account()
        self.add_entry(date='1/1/2008', description='Salary', increase='1500.00')
        self.mainwindow.select_balance_sheet()
    
    def test_delta_perc(self):
        # When the balance at the start is negative, don't display a delta %
        eq_(self.bsheet.net_worth.delta_perc, '---')
    

class OneExcludedAccount(_AccountsAndEntries):
    def setUp(self):
        _AccountsAndEntries.setUp(self)
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.toggle_excluded()
    
    def test_gui_calls(self):
        # account exclusion refreshes the sheet
        self.check_gui_calls(self.bsheet_gui, ['refresh'])
    
    def test_save_and_load(self):
        # account exclusion is persistent
        newdoc = self.save_and_load(newapp=False)
        app = TestApp(app=self.app, doc=newdoc)
        assert app.bsheet.assets[1].is_excluded
    
    def test_values(self):
        # Excluding an account removes its amount from the totals and blanks its own amounts
        eq_(self.bsheet.assets[1].start, '')
        eq_(self.bsheet.assets[1].end, '')
        eq_(self.bsheet.assets[1].delta, '')
        eq_(self.bsheet.assets[1].delta_perc, '')
        eq_(self.bsheet.assets.start, '0.00')
        eq_(self.bsheet.assets.end, '250.00')
        eq_(self.bsheet.assets.delta, '250.00')
        eq_(self.bsheet.assets.delta_perc, '---')
        assert self.bsheet.assets[1].is_excluded
    
