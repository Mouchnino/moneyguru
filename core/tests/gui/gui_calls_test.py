# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-07
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# GUI calls are often made under the same conditions for multiple guis. Duplicating that condition
# in every test unit can get tedious, so this test unit is a "theme based" unit which tests calls
# made to GUIs' view.

from hsutil.currency import EUR

from ...document import FilterType
from ...model.account import AccountType
from ..base import TestCase, TestApp

#--- No Setup
def test_initial_gui_calls():
    app = TestApp()
    app.check_gui_calls(app.bsheet_gui, ['refresh'])
    app.check_gui_calls(app.mainwindow_gui, ['refresh_date_range_selector', 'show_balance_sheet'])

#--- Cleared GUI calls
def app_cleared_gui_calls():
    app = TestApp()
    app.clear_gui_calls()
    return app

def test_add_group():
    # Adding a group refreshes the view and goes into edit mode.
    app = app_cleared_gui_calls()
    app.bsheet.add_account_group()
    expected_calls = ['stop_editing', 'start_editing', 'refresh', 'update_selection']
    app.check_gui_calls(app.bsheet_gui, expected_calls)
    # When doing an action that modifies the undo stack, refresh_undo_actions is called
    # (we're not testing all actions on this one because it's just tiresome and, frankly, a
    # little silly, but assume that all events broadcasted when the undo stack is changed
    # have been connected)
    app.check_gui_calls(app.mainwindow_gui, ['refresh_undo_actions'])

def test_add_transaction():
    # Adding a transaction causes a refresh_undo_actions() gui call and the tview's totals to
    # be updated.
    app = app_cleared_gui_calls()
    app.mainwindow.select_transaction_table()
    app.clear_gui_calls()
    app.ttable.add()
    app.ttable[0].description = 'foobar'
    app.ttable.save_edits()
    app.check_gui_calls(app.mainwindow_gui, ['refresh_undo_actions'])
    app.check_gui_calls(app.tview_gui, ['refresh_totals'])

def test_change_default_currency():
    # When the default currency is changed, all gui refresh themselves
    app = app_cleared_gui_calls()
    app.app.default_currency = EUR
    app.check_gui_calls(app.bsheet_gui, ['refresh'])
    app.check_gui_calls(app.nwgraph_gui, ['refresh'])
    app.check_gui_calls(app.apie_gui, ['refresh'])
    app.check_gui_calls(app.lpie_gui, ['refresh'])
    # but not if it stays the same
    app.app.default_currency = EUR
    app.check_gui_calls_partial(app.bsheet_gui, not_expected=['refresh'])

def test_new_budget():
    # Repeat options must be updated upon panel load
    app = app_cleared_gui_calls()
    app.add_account('income', account_type=AccountType.Income) # we need an account for the panel to load
    app.mainwindow.select_budget_table()
    app.mainwindow.new_item()
    app.check_gui_calls_partial(app.bpanel_gui, ['refresh_repeat_options'])

def test_new_schedule():
    # Repeat options and mct notices must be updated upon panel load
    app = app_cleared_gui_calls()
    app.mainwindow.select_schedule_table()
    app.mainwindow.new_item()
    expected = ['refresh_for_multi_currency', 'refresh_repeat_options']
    app.check_gui_calls_partial(app.scpanel_gui, expected)

def test_show_transaction_table():
    # tview's totals label is refreshed upon connecting.
    app = app_cleared_gui_calls()
    app.mainwindow.show_transaction_table()
    app.check_gui_calls(app.tview_gui, ['refresh_totals'])

def test_sort_table():
    # sorting a table refreshes it.
    app = app_cleared_gui_calls()
    app.mainwindow.select_transaction_table()
    app.clear_gui_calls()
    app.ttable.sort_by('description')
    app.check_gui_calls(app.ttable_gui, ['refresh'])

def test_ttable_add_and_cancel():
    # gui calls on the ttable are correctly made
    app = app_cleared_gui_calls()
    app.mainwindow.select_transaction_table()
    app.clear_gui_calls()
    app.ttable.add()
    # stop_editing must happen first
    expected = ['stop_editing', 'refresh', 'start_editing']
    app.check_gui_calls(app.ttable_gui, expected, verify_order=True)
    app.ttable.cancel_edits()
    # again, stop_editing must happen first
    expected = ['stop_editing', 'refresh']
    app.check_gui_calls(app.ttable_gui, expected, verify_order=True)

def test_show_account():
    # on show_account() totals are refreshed
    app = app_cleared_gui_calls()
    app.add_account()
    app.clear_gui_calls()
    app.mainwindow.show_account()
    app.check_gui_calls_partial(app.aview_gui, ['refresh_totals'])

#--- On transaction view
def app_on_transaction_view():
    app = TestApp()
    app.mainwindow.show_transaction_table()
    app.clear_gui_calls()
    return app

def test_changing_date_range_refreshes_transaction_totals():
    # totals label should be refreshed when the date range changes
    app = app_on_transaction_view()
    app.doc.select_quarter_range()
    app.check_gui_calls(app.tview_gui, ['refresh_totals'])

#--- One account
def app_one_account():
    app = TestApp()
    app.add_account('foobar')
    app.mainwindow.show_account()
    app.clear_gui_calls()
    return app
    
def test_add_entry():
    # Before adding a new entry, make sure the entry table is not in edition mode. Then, start 
    # editing the new entry. Adding an entry also refreshes account totals.
    app = app_one_account()
    app.add_entry()
    app.check_gui_calls_partial(app.etable_gui, ['stop_editing', 'refresh', 'start_editing'])
    app.check_gui_calls_partial(app.aview_gui, ['refresh_totals'])

def test_change_aview_filter():
    # Changing aview's filter type updates the totals
    app = app_one_account()
    app.efbar.filter_type = FilterType.Reconciled
    app.check_gui_calls(app.aview_gui, ['refresh_totals'])

def test_changing_date_range_refreshes_account_totals():
    # totals label should be refreshed when the date range changes
    app = app_one_account()
    app.doc.select_quarter_range()
    app.check_gui_calls(app.aview_gui, ['refresh_totals'])

def test_delete_entry():
    app = app_one_account()
    app.add_entry()
    app.clear_gui_calls()
    app.mainwindow.delete_item()
    app.check_gui_calls_partial(app.aview_gui, ['refresh_totals'])

def test_jump_to_account():
    app = app_one_account()
    app.mainwindow.jump_to_account()
    app.check_gui_calls(app.alookup_gui, ['refresh', 'show'])
    app.alookup.search_query = 'foo'
    app.check_gui_calls(app.alookup_gui, ['refresh'])
    app.alookup.go()
    app.check_gui_calls(app.alookup_gui, ['hide'])

class OneTransaction(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_txn()
        self.clear_gui_calls()
    
    def test_delete_transaction(self):
        # Deleting a transaction refreshes the totals label
        self.mainwindow.delete_item()
        self.check_gui_calls(self.tview_gui, ['refresh_totals'])
    
    def test_change_tview_filter(self):
        # Changing tview's filter type updates the totals
        self.tfbar.filter_type = FilterType.Reconciled
        self.check_gui_calls(self.tview_gui, ['refresh_totals'])
    

class LoadFileWithBalanceSheetSelected(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
        self.document.load_from_xml(self.filepath('moneyguru', 'simple.moneyguru'))
    
    def test_views_are_refreshed(self):
        # view.refresh() is called on file load
        self.check_gui_calls_partial(self.bsheet_gui, ['refresh'])
        self.check_gui_calls_partial(self.nwgraph_gui, ['refresh'])
    

class TransactionBetweenIncomeAndExpense(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('income', account_type=AccountType.Income)
        self.add_account('expense', account_type=AccountType.Expense)
        self.add_txn(from_='income', to='expense', amount='42')
        self.clear_gui_calls()
    
    def test_etable_show_transfer_account(self):
        # show_transfer_account() correctly refreshes the gui even if the graph type deosn't change.
        self.show_account('income')
        self.clear_gui_calls()
        self.etable.show_transfer_account()
        self.check_gui_calls(self.etable_gui, ['show_selected_row', 'refresh'])
        self.check_gui_calls(self.bargraph_gui, ['refresh'])
    

class TransactionBetweenAssetAndLiability(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('asset', account_type=AccountType.Asset)
        self.add_account('liability', account_type=AccountType.Liability)
        self.add_txn(from_='liability', to='asset', amount='42')
        self.clear_gui_calls()
    
    def test_etable_show_transfer_account(self):
        # show_transfer_account() correctly refreshes the gui even if the graph type deosn't change.
        self.show_account('asset')
        self.clear_gui_calls()
        self.etable.show_transfer_account()
        self.check_gui_calls(self.etable_gui, ['show_selected_row', 'refresh'])
        self.check_gui_calls(self.balgraph_gui, ['refresh'])
    

#--- Transaction with panel loaded
def app_transaction_with_panel_loaded():
    app = TestApp()
    app.add_txn('20/02/2010', from_='foo', to='bar', amount='42')
    app.tpanel.load()
    app.clear_gui_calls()
    return app

def test_change_txn_amount():
    # Changing the panel's amount results in a refresh_amount call
    app = app_transaction_with_panel_loaded()
    app.tpanel.amount = '23'
    app.check_gui_calls_partial(app.tpanel_gui, ['refresh_amount'])

def test_change_txn_amount_through_splits():
    # Changing the transaction's amount through the splits updates the Amount field.
    app = app_transaction_with_panel_loaded()
    app.stable[0].debit = '54'
    app.stable.save_edits()
    app.check_gui_calls_partial(app.tpanel_gui, ['refresh_amount'])

def test_delete_split():
    # Deleting a split calls refresh_amount. This is in caste the txn is multi-currency.
    app = app_transaction_with_panel_loaded()
    app.stable.delete()
    app.check_gui_calls_partial(app.tpanel_gui, ['refresh_amount'])

def test_move_split():
    # The split table is refreshed after a move
    app = app_transaction_with_panel_loaded()
    app.stable.move_split(0, 1)
    app.check_gui_calls_partial(app.stable_gui, ['refresh'])
