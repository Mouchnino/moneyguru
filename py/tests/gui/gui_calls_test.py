# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-07
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# GUI calls are often made under the same conditions for multiple guis. Duplicating that condition
# in every test unit can get tedious, so this test unit is a "theme based" unit which tests calls
# made to GUIs' view.

from hsutil.currency import EUR

from ...model.account import INCOME
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
        # Adding a transaction causes a refresh_undo_actions() gui call
        self.mainwindow.select_transaction_table()
        self.clear_gui_calls()
        self.ttable.add()
        self.ttable[0].description = 'foobar'
        self.ttable.save_edits()
        self.check_gui_calls(self.mainwindow_gui, ['refresh_undo_actions'])
    
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
        self.add_account('income', account_type=INCOME) # we need an account for the panel to load
        self.mainwindow.select_budget_table()
        self.mainwindow.new_item()
        self.check_gui_calls_partial(self.bpanel_gui, ['refresh_repeat_options'])
    
    def test_new_schedule(self):
        # Repeat options must be updated upon panel load
        self.mainwindow.select_schedule_table()
        self.mainwindow.new_item()
        self.check_gui_calls_partial(self.scpanel_gui, ['refresh_repeat_options'])
    
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
    

class LoadFileWithBalanceSheetSelected(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
        self.document.load_from_xml(self.filepath('xml', 'moneyguru.xml'))
    
    def test_views_are_refreshed(self):
        # view.refresh() is called on file load
        self.check_gui_calls_partial(self.bsheet_gui, ['refresh'])
        self.check_gui_calls_partial(self.nwgraph_gui, ['refresh'])
    
