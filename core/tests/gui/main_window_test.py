# Created By: Eric Mc Sween
# Created On: 2008-07-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from ..base import TestApp, with_app
from ...const import ViewType
from ...model.date import YearRange

#--- Pristine
def app_cleared_gui_calls():
    app = TestApp()
    app.clear_gui_calls()
    return app

@with_app(app_cleared_gui_calls)
def test_change_date_range(app):
    app.doc.date_range = app.doc.date_range.prev()
    expected_calls = ['refresh', 'animate_backward']
    app.check_gui_calls(app.drsel_gui, expected_calls)
    app.check_gui_calls_partial(app.bsheet_gui, ['refresh'])
    app.check_gui_calls(app.nwgraph_gui, ['refresh'])
    app.check_gui_calls_partial(app.balgraph_gui, not_expected=['refresh'])
    app.check_gui_calls_partial(app.bargraph_gui, not_expected=['refresh'])

@with_app(app_cleared_gui_calls)
def test_current_view_index(app):
    # The main window has a `current_view_index` property which indicate which view is currently
    # selected.
    view_seq = [0, 1, 2, 4, 5] # we skip the account view because there's no shown account
    for index in view_seq:
        eq_(app.mw.current_view_index, index)
        app.mw.select_next_view()
    # we can't go further
    app.mw.select_next_view()
    eq_(app.mw.current_view_index, 5)
    for index in reversed(view_seq):
        eq_(app.mw.current_view_index, index)
        app.mw.select_previous_view()
    # we can't go further
    app.mw.select_previous_view()
    eq_(app.mw.current_view_index, 0)

@with_app(app_cleared_gui_calls)
def test_select_ttable_on_sfield_query(app):
    # Setting a value in the search field selects the ttable.
    app.sfield.query = 'foobar'
    eq_(app.mw.current_view_index, 2)

@with_app(app_cleared_gui_calls)
def test_view_count(app):
    # the view_count property returns the number of available views.
    eq_(app.mw.view_count, 6)

@with_app(app_cleared_gui_calls)
def test_current_types(app):
    # View types are correct
    eq_(app.mw.view_type(0), ViewType.NetWorth)
    eq_(app.mw.view_type(1), ViewType.Profit)
    eq_(app.mw.view_type(2), ViewType.Transaction)
    eq_(app.mw.view_type(3), ViewType.Account)
    eq_(app.mw.view_type(4), ViewType.Schedule)
    eq_(app.mw.view_type(5), ViewType.Budget)

#--- Asset and Income accounts
def app_asset_and_income_accounts():
    app = TestApp()
    app.add_account('Checking')
    app.doc.show_selected_account()
    app.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00')
    app.doc.date_range = YearRange(date(2007, 1, 1))
    app.clear_gui_calls()
    return app

@with_app(app_asset_and_income_accounts)
def test_delete_account(app):
    # deleting a non-empty account shows the account reassign panel
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.clear_gui_calls()
    app.bsheet.delete()
    app.check_gui_calls(app.mainwindow_gui, ['show_account_reassign_panel'])

@with_app(app_asset_and_income_accounts)
def test_navigate_back(app):
    # navigate_back() shows the appropriate sheet depending on which account entry table shows
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    app.clear_gui_calls()
    app.mw.navigate_back()
    eq_(app.mw.current_view_index, 0)
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[0]
    app.istatement.show_selected_account()
    app.clear_gui_calls()
    app.mw.navigate_back()
    eq_(app.mw.current_view_index, 1)

@with_app(app_asset_and_income_accounts)
def test_select_next_previous_view(app):
    # Now that an account has been shown, the Account view is part of the view cycle
    app.mw.select_previous_view()
    eq_(app.mw.current_view_index, 2)
    app.mw.select_next_view()
    eq_(app.mw.current_view_index, 3)
    app.mw.select_next_view()
    eq_(app.mw.current_view_index, 4)
    app.mw.select_previous_view()
    eq_(app.mw.current_view_index, 3)

@with_app(app_asset_and_income_accounts)
def test_show_account_when_in_sheet(app):
    # When a sheet is selected, show_account() shows the selected account.
    app.mw.select_balance_sheet()
    app.clear_gui_calls()
    app.mw.show_account()
    eq_(app.mw.current_view_index, 3)
    app.mw.select_income_statement()
    app.clear_gui_calls()
    app.mw.show_account()
    eq_(app.mw.current_view_index, 3)

@with_app(app_asset_and_income_accounts)
def test_switch_views(app):
    # Views shown in the main window depend on what's selected in the account tree.
    app.mw.select_income_statement()
    eq_(app.mw.current_view_index, 1)
    app.istatement.selected = app.istatement.income[0]
    app.istatement.show_selected_account()
    eq_(app.mw.current_view_index, 3)
    expected = ['refresh_totals', 'show_bar_graph', 'refresh_reconciliation_button']
    app.check_gui_calls(app.aview_gui, expected)
    app.mainwindow.select_balance_sheet()
    eq_(app.mw.current_view_index, 0)
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    eq_(app.mw.current_view_index, 3)
    expected = ['refresh_totals', 'show_line_graph', 'refresh_reconciliation_button']
    app.check_gui_calls(app.aview_gui, expected)
    app.mainwindow.select_transaction_table()
    eq_(app.mw.current_view_index, 2)

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
    eq_(app.doc.shown_account.name, 'second')

@with_app(app_one_transaction)
def test_show_account_when_in_ttable(app):
    app.mw.show_account()
    eq_(app.mw.current_view_index, 3)
    eq_(app.doc.shown_account.name, 'first')
