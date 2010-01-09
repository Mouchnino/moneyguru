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
from ..base import TestCase

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.check_gui_calls(self.bsheet_gui, ['refresh'])
        self.check_gui_calls(self.mainwindow_gui, ['refresh_date_range_selector', 'show_balance_sheet'])
        self.clear_gui_calls()
    
    def test_add_group(self):
        # Adding a group refreshes the view and goes into edit mode.
        self.bsheet.add_account_group()
        expected_calls = ['stop_editing', 'start_editing', 'refresh', 'update_selection']
        self.check_gui_calls(self.bsheet_gui, expected_calls)
        # When doing an action that modifies the undo stack, refresh_undo_actions is called
        # (we're not testing all actions on this one because it's just tiresome and, frankly, a
        # little silly, but assume that all events broadcasted when the undo stack is changed
        # have been connected)
        self.check_gui_calls(self.mainwindow_gui, ['refresh_undo_actions'])
    
    def test_add_transaction(self):
        # Adding a transaction causes a refresh_undo_actions() gui call and the tview's totals to
        # be updated.
        self.mainwindow.select_transaction_table()
        self.clear_gui_calls()
        self.ttable.add()
        self.ttable[0].description = 'foobar'
        self.ttable.save_edits()
        self.check_gui_calls(self.mainwindow_gui, ['refresh_undo_actions'])
        self.check_gui_calls(self.tview_gui, ['refresh_totals'])
    
    def test_change_default_currency(self):
        # When the default currency is changed, all gui refresh themselves
        self.app.default_currency = EUR
        self.check_gui_calls(self.bsheet_gui, ['refresh'])
        self.check_gui_calls(self.nwgraph_gui, ['refresh'])
        self.check_gui_calls(self.apie_gui, ['refresh'])
        self.check_gui_calls(self.lpie_gui, ['refresh'])
        # but not if it stays the same
        self.app.default_currency = EUR
        self.check_gui_calls_partial(self.bsheet_gui, not_expected=['refresh'])
    
    def test_new_budget(self):
        # Repeat options must be updated upon panel load
        self.add_account('income', account_type=AccountType.Income) # we need an account for the panel to load
        self.mainwindow.select_budget_table()
        self.mainwindow.new_item()
        self.check_gui_calls_partial(self.bpanel_gui, ['refresh_repeat_options'])
    
    def test_new_schedule(self):
        # Repeat options must be updated upon panel load
        self.mainwindow.select_schedule_table()
        self.mainwindow.new_item()
        self.check_gui_calls_partial(self.scpanel_gui, ['refresh_repeat_options'])
    
    def test_show_transaction_table(self):
        # tview's totals label is refreshed upon connecting.
        self.mainwindow.show_transaction_table()
        self.check_gui_calls(self.tview_gui, ['refresh_totals'])
    
    def test_sort_table(self):
        # sorting a table refreshes it.
        self.mainwindow.select_transaction_table()
        self.clear_gui_calls()
        self.ttable.sort_by('description')
        self.check_gui_calls(self.ttable_gui, ['refresh'])
    
    def test_ttable_add_and_cancel(self):
        # gui calls on the ttable are correctly made
        self.mainwindow.select_transaction_table()
        self.clear_gui_calls()
        self.ttable.add()
        # stop_editing must happen first
        expected = ['stop_editing', 'refresh', 'start_editing']
        self.check_gui_calls(self.ttable_gui, expected, verify_order=True)
        self.ttable.cancel_edits()
        # again, stop_editing must happen first
        expected = ['stop_editing', 'refresh']
        self.check_gui_calls(self.ttable_gui, expected, verify_order=True)
    

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
        self.check_gui_calls(self.etable_gui, ['refresh'])
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
        self.check_gui_calls(self.etable_gui, ['refresh'])
        self.check_gui_calls(self.balgraph_gui, ['refresh'])
    