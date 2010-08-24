# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license



from hsutil.testutil import eq_

from ...model.account import AccountType
from ..base import TestApp, with_app

#--- Two entries
def app_two_entries():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('11/07/2008', 'first', increase='42')
    app.add_entry('12/07/2008', 'second', decrease='12')
    return app

@with_app(app_two_entries)
def test_totals_one_selected(app):
    # the totals line shows totals for selected entries
    expected = "1 out of 2 selected. Increase: 0.00 Decrease: 12.00"
    eq_(app.mw.status_line, expected)

@with_app(app_two_entries)
def test_totals_two_selected(app):
    # the totals line shows totals for selected entries
    app.etable.select([0, 1])
    expected = "2 out of 2 selected. Increase: 42.00 Decrease: 12.00"
    eq_(app.mw.status_line, expected)

@with_app(app_two_entries)
def test_totals_with_unicode_amount_format(app):
    # it seems that some people have some weird separator in their settings, and there was a
    # UnicodeEncodeError in the status line formatting.
    app.app._decimal_sep = '\xa0'
    app.mw.select_transaction_table() # force a refresh
    app.mw.select_entry_table()
    expected = "1 out of 2 selected. Increase: 0\xa000 Decrease: 12\xa000"
    eq_(app.mw.status_line, expected)

#--- Asset Shown
def app_asset_shown():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    return app

@with_app(app_asset_shown)
def test_can_toggle_reconciliation_mode_with_asset_shown(app):
    # When an asset is shown, reconciliation mode can be toggled
    assert app.aview.can_toggle_reconciliation_mode

#--- Expense Shown
def app_expense_shown():
    app = TestApp()
    app.add_account(account_type=AccountType.Expense)
    app.mw.show_account()
    return app

@with_app(app_expense_shown)
def test_can_toggle_reconciliation_mode_with_expense_shown(app):
    # When an asset is shown, reconciliation mode can't be toggled
    assert not app.aview.can_toggle_reconciliation_mode