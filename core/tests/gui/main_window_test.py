# Created By: Eric Mc Sween
# Created On: 2008-07-12
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...const import PaneType, PaneArea
from ...model.account import AccountType
from ...model.date import YearRange

#--- Pristine
@with_app(TestApp)
def test_close_pane(app):
    # closing a view removes it from main window's subviews
    app.mw.current_pane_index = 2
    app.clear_gui_calls()
    app.mw.close_pane(3)
    eq_(app.mw.pane_count, 4)
    eq_(app.mw.pane_type(3), PaneType.Budget)
    eq_(app.mw.current_pane_index, 2)
    app.check_gui_calls(app.mainwindow_gui, ['view_closed'])

@with_app(TestApp)
def test_close_pane_index_lower_than_selected(app):
    # when a view with an index lower than the selected view is closed, the selected view stays the
    # same.
    app.mw.current_pane_index = 2
    app.clear_gui_calls()
    app.mw.close_pane(1)
    # The current index was decremented by one to follow the current index.
    eq_(app.mw.current_pane_index, 1)
    # Event though the view itself didn't change, we still have a change_current_pane call so that
    # the selected view index changed.
    app.check_gui_calls(app.mainwindow_gui, ['view_closed', 'change_current_pane'])

@with_app(TestApp)
def test_close_pane_when_selected(app):
    # closing the selected view adjusts the current view index if appropriate
    app.mw.current_pane_index = 3
    app.clear_gui_calls()
    app.mw.close_pane(3)
    eq_(app.mw.current_pane_index, 3) # We stay at 4 because it's appropriate
    # Although the view index stayed the same, the view still changed, so the GUI needs to change.
    app.check_gui_calls(app.mainwindow_gui, ['view_closed', 'change_current_pane', 'refresh_status_line'])
    app.mw.close_pane(3)
    eq_(app.mw.current_pane_index, 2)

@with_app(TestApp)
def test_current_pane_index(app):
    # The main window has a `current_pane_index` property which indicate which view is currently
    # selected.
    for index in range(5):
        eq_(app.mw.current_pane_index, index)
        app.mw.select_next_view()
    # we can't go further
    app.mw.select_next_view()
    eq_(app.mw.current_pane_index, 4)
    for index in reversed(range(5)):
        eq_(app.mw.current_pane_index, index)
        app.mw.select_previous_view()
    # we can't go further
    app.mw.select_previous_view()
    eq_(app.mw.current_pane_index, 0)

@with_app(TestApp)
def test_initial_panes(app):
    eq_(app.mw.pane_count, 5)
    eq_(app.mw.pane_label(0), "Net Worth")
    eq_(app.mw.pane_label(1), "Profit & Loss")
    eq_(app.mw.pane_label(2), "Transactions")
    eq_(app.mw.pane_label(3), "Schedules")
    eq_(app.mw.pane_label(4), "Budgets")
    eq_(app.mw.pane_type(0), PaneType.NetWorth)
    eq_(app.mw.pane_type(1), PaneType.Profit)
    eq_(app.mw.pane_type(2), PaneType.Transaction)
    eq_(app.mw.pane_type(3), PaneType.Schedule)
    eq_(app.mw.pane_type(4), PaneType.Budget)

@with_app(TestApp)
def test_move_pane(app):
    # moving a pane takes a pane at a specified index and moves it to the dest index
    app.mw.move_pane(2, 1)
    eq_(app.mw.pane_label(1), "Transactions")
    eq_(app.mw.pane_label(2), "Profit & Loss")
    # when moving a pane, the dest index is the index *with* the pane at its original position,
    # *not* the index with the pane removed from the list.
    app.mw.move_pane(2, 3)
    eq_(app.mw.pane_label(2), "Schedules")
    eq_(app.mw.pane_label(3), "Profit & Loss")
    # When the pane index is the same as the dest index, we do nothing.
    app.mw.move_pane(2, 2)
    eq_(app.mw.pane_label(1), "Transactions")
    eq_(app.mw.pane_label(2), "Schedules")
    eq_(app.mw.pane_label(3), "Profit & Loss")

@with_app(TestApp)
def test_move_pane_before_selected(app):
    # When a non-selected pane is moved before the selected one, update the selected index
    app.mw.move_pane(1, 0)
    eq_(app.mw.current_pane_index, 1)

@with_app(TestApp)
def test_move_pane_selected(app):
    # When the moved pane is selected, the selection follows the pane.
    app.mw.move_pane(0, 3)
    eq_(app.mw.current_pane_index, 3)

@with_app(TestApp)
def test_selected_account_is_updated_on_nonrevalidating_show(app):
    # When navigating between sheet-panes, the selected account (used for show_account and apanel)
    # is correctly updated
    app.add_account('Asset')
    app.add_account('Income', account_type=AccountType.Income)
    app.mw.select_balance_sheet()
    app.mw.select_income_statement() # no revalidation since nothing has changed
    app.mw.show_account()
    app.check_current_pane(PaneType.Account, account_name='Income')

@with_app(TestApp)
def test_select_pane_of_type_creates_new_pane_if_needed(app):
    # calling select_pane_of_type() creates a new pane if needed
    app.mw.close_pane(0) # net worth
    app.mw.select_pane_of_type(PaneType.NetWorth)
    eq_(app.mw.pane_count, 5)
    app.check_current_pane(PaneType.NetWorth)

@with_app(TestApp)
def test_select_ttable_on_sfield_query(app):
    # Setting a value in the search field selects the ttable.
    app.sfield.query = 'foobar'
    eq_(app.mw.current_pane_index, 2)

@with_app(TestApp)
def test_dont_close_last_pane(app):
    # if close_pane() is called with only one pane left, don't do anything.
    while (app.mw.pane_count > 1):
        app.mw.close_pane(0)
    app.mw.close_pane(0) # no crash
    eq_(app.mw.pane_count, 1)

@with_app(TestApp)
def test_column_menu_attributes(app):
    # The column menu depends on the selected pane and shows the display attribute of optional
    # columns.
    app.show_nwview()
    expected = [("Account #", False), ("Start", True), ("Change", False), ("Change %", False),
        ("Budgeted", True)]
    eq_(app.mw.column_menu_items(), expected)
    app.mw.toggle_column_menu_item(0)
    expected[0] = ("Account #", True)
    eq_(app.mw.column_menu_items(), expected)

@with_app(TestApp)
def test_column_visibility_change_actually_changes_visibility(app):
    # Changing the value of a column visibility in view options actually changes visibility
    app.show_tview()
    app.set_column_visible('description', False)
    assert not app.ttable.columns.column_is_visible('description')

@with_app(TestApp)
def test_change_view_options_while_editing(app):
    # When a table is in editing mode and that a column visibility is changed, we have to tell the
    # gui to stop editing, or else we end up in a state where the core thinks it's editing when the
    # GUI isn't.
    app.show_tview()
    app.mw.new_item()
    app.ttable.payee = 'something' # in editing mode
    app.set_column_visible('description', False)
    assert app.ttable.edited is None

#--- Cleared GUI calls
def app_cleared_gui_calls():
    app = TestApp()
    app.clear_gui_calls()
    return app

@with_app(app_cleared_gui_calls)
def test_change_date_range(app):
    app.doc.date_range = app.doc.date_range.prev()
    expected_calls = ['refresh', 'animate_backward']
    app.drsel.view.check_gui_calls(expected_calls)
    app.check_gui_calls_partial(app.bsheet_gui, ['refresh'])
    app.check_gui_calls(app.nwgraph_gui, ['refresh'])
    app.check_gui_calls_partial(app.balgraph_gui, not_expected=['refresh'])
    app.check_gui_calls_partial(app.bargraph_gui, not_expected=['refresh'])

@with_app(app_cleared_gui_calls)
def test_new_tab(app):
    app.mw.new_tab()
    eq_(app.mw.pane_count, 6)
    app.check_current_pane(PaneType.Empty)
    app.check_gui_calls(app.mainwindow_gui, ['change_current_pane', 'refresh_panes', 'refresh_status_line'])
    app.emptyview.select_pane_type(PaneType.Profit)
    app.check_current_pane(PaneType.Profit)
    app.check_gui_calls(app.mainwindow_gui, ['change_current_pane', 'refresh_panes', 'refresh_status_line'])

@with_app(app_cleared_gui_calls)
def test_toggle_area_visibility(app):
    app.mw.toggle_area_visibility(PaneArea.BottomGraph)
    app.nwview.view.check_gui_calls(['update_visibility'])
    # It sends the message to the main window as well (so it can update its buttons)
    app.mw.view.check_gui_calls(['update_area_visibility'])
    # Also update the visibility of other views when we select them
    app.show_pview()
    app.pview.view.check_gui_calls(['update_visibility'])

#--- One account
def app_one_account():
    app = TestApp()
    app.add_account("foo")
    app.clear_gui_calls()
    return app

@with_app(app_one_account)
def test_rename_opened_account_changes_tab_label(app):
    # Renaming the account with an opened tab renames that tab.
    app.mw.show_account()
    index = app.mw.current_pane_index
    app.mw.select_balance_sheet()
    app.clear_gui_calls()
    app.bsheet.selected.name = 'renamed'
    app.bsheet.save_edits()
    eq_(app.mw.pane_label(index), 'renamed')
    app.check_gui_calls(app.mainwindow_gui, ['refresh_panes', 'refresh_undo_actions'])

@with_app(app_one_account)
def test_show_account_opens_a_new_tab(app):
    # Showing an account opens a new tab with the account shown in it.
    app.mw.show_account()
    eq_(app.mw.pane_count, 6)
    eq_(app.mw.current_pane_index, 5)
    eq_(app.mw.pane_type(5), PaneType.Account)
    eq_(app.mw.pane_label(5), "foo")
    expected = ['refresh_panes', 'change_current_pane']
    app.check_gui_calls_partial(app.mainwindow_gui, expected, verify_order=True)

#--- Asset and Income accounts with txn
def app_asset_and_income_accounts_with_txn():
    app = TestApp()
    app.add_account('Checking')
    app.mw.show_account()
    app.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00')
    app.doc.date_range = YearRange(date(2007, 1, 1))
    app.clear_gui_calls()
    return app

@with_app(app_asset_and_income_accounts_with_txn)
def test_close_pane_of_autocleaned_accounts(app):
    # When an account is auto cleaned, close its pane if it's opened
    app.etable.show_transfer_account() # the Salary account, which is auto-created
    app.etable.show_transfer_account() # We're back on the Checking account
    app.etable.delete() # the Salary pane is supposed to be closed.
    eq_(app.mw.pane_count, 6)
    eq_(app.mw.current_pane_index, 5) # we stay on the current index

@with_app(app_asset_and_income_accounts_with_txn)
def test_delete_account(app):
    # deleting a non-empty account shows the account reassign panel
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.clear_gui_calls()
    app.bsheet.delete()
    app.arpanel.view.check_gui_calls(['pre_load', 'post_load'])

@with_app(app_asset_and_income_accounts_with_txn)
def test_navigate_back(app):
    # navigate_back() shows the appropriate sheet depending on which account entry table shows
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    app.clear_gui_calls()
    app.mw.navigate_back()
    eq_(app.mw.current_pane_index, 0)
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[0]
    app.istatement.show_selected_account()
    app.clear_gui_calls()
    app.mw.navigate_back()
    eq_(app.mw.current_pane_index, 1)

@with_app(app_asset_and_income_accounts_with_txn)
def test_show_account_when_in_sheet(app):
    # When a sheet is selected, show_account() shows the selected account. If the account already
    # has a tab opened, re-use that tab.
    app.mw.select_balance_sheet()
    app.clear_gui_calls()
    app.mw.show_account()
    eq_(app.mw.current_pane_index, 5) # The tab opened in setup is re-used
    app.mw.select_income_statement()
    app.clear_gui_calls()
    app.mw.show_account()
    eq_(app.mw.current_pane_index, 6) # a new tab is opened for this one

@with_app(app_asset_and_income_accounts_with_txn)
def test_switch_panes_through_show_account(app):
    # Views shown in the main window depend on what's selected in the account tree.
    app.mw.select_income_statement()
    eq_(app.mw.current_pane_index, 1)
    app.istatement.selected = app.istatement.income[0]
    app.istatement.show_selected_account()
    eq_(app.mw.current_pane_index, 6)
    expected = ['show_bar_graph', 'refresh_reconciliation_button']
    app.check_gui_calls_partial(app.aview.view, expected)
    app.mainwindow.select_balance_sheet()
    eq_(app.mw.current_pane_index, 0)
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    eq_(app.mw.current_pane_index, 5)
    expected = ['show_line_graph', 'refresh_reconciliation_button']
    app.check_gui_calls_partial(app.aview.view, expected)
    app.mainwindow.select_transaction_table()
    eq_(app.mw.current_pane_index, 2)

@with_app(app_asset_and_income_accounts_with_txn)
def test_switch_panes_through_pane_index(app):
    app.etable.show_transfer_account()
    eq_(app.mw.pane_count, 7) # Now, the two last views are our 2 accounts
    app.mw.select_previous_view()
    # etable has change its values
    eq_(app.etable[0].transfer, "Salary")
    app.mw.select_next_view()
    # and again
    eq_(app.etable[0].transfer, "Checking")

#--- One transaction
def app_one_transaction():
    app = TestApp()
    app.add_account('first')
    app.add_txn(from_='first', to='second', amount='42')
    app.clear_gui_calls()
    return app

@with_app(app_one_transaction)
def test_show_account_when_in_etable(app):
    app.show_account('first')
    app.mw.show_account()
    app.check_current_pane(PaneType.Account, 'second')

@with_app(app_one_transaction)
def test_show_account_when_in_ttable(app):
    app.mw.show_account()
    app.check_current_pane(PaneType.Account, 'first')
