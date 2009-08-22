# Created By: Eric Mc Sween
# Created On: 2008-07-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from ..base import TestCase
from ...model.date import YearRange

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.check_gui_calls(self.mainwindow_gui, refresh_date_range_selector=1, show_balance_sheet=1)
        self.clear_gui_calls()

    def test_change_date_range(self):
        self.document.date_range = self.document.date_range.prev()
        self.check_gui_calls(self.mainwindow_gui, refresh_date_range_selector=1, 
                             animate_date_range_backward=1)
        self.check_gui_calls_partial(self.bsheet_gui, refresh=1)
        self.check_gui_calls(self.nwgraph_gui, refresh=1)
        self.check_gui_calls(self.balgraph_gui) # no refresh, it is disconnected
        self.check_gui_calls(self.bargraph_gui) # no refresh, it is disconnected
    
    def test_gui_calls(self):
        # the main window sends it's view calls on *connect*, not on init
        self.mainwindow.disconnect()
        self.mainwindow.connect()
        self.check_gui_calls(self.mainwindow_gui, refresh_date_range_selector=1)
    
    def test_select_next_previous_view(self):
        self.mainwindow.select_next_view()
        self.check_gui_calls(self.mainwindow_gui, show_income_statement=1)
        self.mainwindow.select_next_view()
        self.check_gui_calls(self.mainwindow_gui, show_transaction_table=1)
        self.mainwindow.select_next_view()
        self.check_gui_calls(self.mainwindow_gui, show_schedule_table=1)
        self.mainwindow.select_next_view()
        self.check_gui_calls(self.mainwindow_gui, show_budget_table=1)
        self.mainwindow.select_previous_view()
        self.check_gui_calls(self.mainwindow_gui, show_schedule_table=1)
        self.mainwindow.select_previous_view()
        self.check_gui_calls(self.mainwindow_gui, show_transaction_table=1)
        self.mainwindow.select_previous_view()
        self.check_gui_calls(self.mainwindow_gui, show_income_statement=1)
    
    def test_select_ttable_on_sfield_query(self):
        """Setting a value in the search field selects the ttable"""
        self.sfield.query = 'foobar'
        self.check_gui_calls(self.mainwindow_gui, show_transaction_table=1)
    

class AssetAccountAndIncomeAccount(TestCase):
    """One empty account."""
    def setUp(self):
        self.create_instances()
        self.clear_gui_calls()
        self.add_account('Checking')
        self.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.clear_gui_calls()
    
    def test_delete_account(self):
        # deleting a non-empty account shows the account reassign panel
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.clear_gui_calls()
        self.bsheet.delete()
        self.check_gui_calls(self.mainwindow_gui, show_account_reassign_panel=1)
    
    def test_navigate_back(self):
        # navigate_back() shows the appropriate sheet depending on which account entry table shows
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.clear_gui_calls()
        self.mainwindow.navigate_back()
        self.check_gui_calls(self.mainwindow_gui, show_balance_sheet=1)
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.clear_gui_calls()
        self.mainwindow.navigate_back()
        self.check_gui_calls(self.mainwindow_gui, show_income_statement=1)
    
    def test_select_next_previous_view(self):
        # Now that an account has been shown, the Account view is part of the view cycle
        self.mainwindow.select_previous_view()
        self.check_gui_calls(self.mainwindow_gui, show_transaction_table=1)
        self.mainwindow.select_next_view()
        self.check_gui_calls(self.mainwindow_gui, show_entry_table=1)
        self.mainwindow.select_next_view()
        self.check_gui_calls(self.mainwindow_gui, show_schedule_table=1)
        self.mainwindow.select_previous_view()
        self.check_gui_calls(self.mainwindow_gui, show_entry_table=1)
    
    def test_switch_views(self):
        """Views shown in the main window depend on what's selected in the account tree."""
        self.mainwindow.select_income_statement()
        self.check_gui_calls(self.mainwindow_gui, show_income_statement=1)
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.check_gui_calls(self.mainwindow_gui, show_entry_table=1, show_bar_graph=1)
        self.mainwindow.select_balance_sheet()
        self.check_gui_calls(self.mainwindow_gui, show_balance_sheet=1)
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.check_gui_calls(self.mainwindow_gui, show_entry_table=1, show_line_graph=1)
        self.mainwindow.select_transaction_table()
        self.check_gui_calls(self.mainwindow_gui, show_transaction_table=1)
    
