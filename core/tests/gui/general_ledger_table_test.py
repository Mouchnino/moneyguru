# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from ...model.account import AccountType
from ..base import TestApp, with_app

#---
@with_app(TestApp)
def test_new_item_in_empty_table(app):
    # Since we have no txn, we have nothing to show in the gltable. Performing new item has no
    # effect.
    app.show_glview()
    app.mw.new_item() # no crash
    eq_(len(app.gltable), 0)

#---
def app_two_sided_txn():
    app = TestApp()
    app.add_accounts('foo', 'bar')
    app.add_txn(description='hello', from_='foo', to='bar', amount='42')
    app.show_glview()
    return app

@with_app(app_two_sided_txn)
def test_delete_entry(app):
    app.gltable.select([4]) # the 'foo' entry of 'hello'
    app.mw.delete_item()
    # both entries were removed
    eq_(len(app.gltable), 0)

@with_app(app_two_sided_txn)
def test_dont_show_empty_accounts(app):
    # When accounts have nothing to show, don't put them in the table.
    app.drsel.select_prev_date_range()
    eq_(len(app.gltable), 0)

@with_app(app_two_sided_txn)
def test_new_entry_with_account_row_selected(app):
    # Adding a new entry when the account row is selected doesn't cause a crash and creates a new
    # entry.
    app.gltable.select([0])
    app.mw.new_item() # no crash
    eq_(len(app.gltable), 7)
    eq_(app.gltable.selected_indexes, [2])

@with_app(app_two_sided_txn)
def test_rows_data_with_two_sided_txn(app):
    # In a general ledger, we end up with 6 lines: 2 account lines (titles), two entry lines as well
    # as two total lines.
    eq_(len(app.gltable), 6)
    ACCOUNT_ROWS = {0, 3}
    BOLD_ROWS = {2, 5}
    EDITABLE_ROWS = {1, 4}
    for i in range(6):
        eq_(app.gltable.is_account_row(i), i in ACCOUNT_ROWS)
        eq_(app.gltable.is_bold_row(i), i in BOLD_ROWS)
        eq_(app.gltable.can_edit_cell('description', i), i in EDITABLE_ROWS)
    eq_(app.gltable[0].account_name, 'bar')
    eq_(app.gltable[3].account_name, 'foo')
    eq_(app.gltable[1].description, 'hello')
    eq_(app.gltable[1].debit, '42.00')
    eq_(app.gltable[4].description, 'hello')
    eq_(app.gltable[4].credit, '42.00')

@with_app(app_two_sided_txn)
def test_set_amount_without_shown_account(app):
    # Previously, setting an amount while mainwindow.shown_account to None resulted in a crash
    app.gltable[1].debit = '42' # no crash
    eq_(app.gltable[1].debit, '42.00')

#---
def app_txns_in_different_date_ranges():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_accounts('foo', 'bar')
    app.add_txn(date='10/08/2010', description='first', from_='foo', to='bar', amount='42')
    app.add_txn(date='10/09/2010', description='second', from_='foo', to='bar', amount='42')
    app.drsel.select_prev_date_range()
    app.show_glview()
    return app

@with_app(app_txns_in_different_date_ranges)
def test_edit_item(app):
    # the table correctly updates txn selection so that when edit item is called, the right txn
    # shown up in the panel.
    app.mw.edit_item()
    eq_(app.tpanel.description, 'first')

@with_app(app_txns_in_different_date_ranges)
def test_only_show_rows_in_date_range(app):
    # Rows that are out of the date range aren't shown.
    eq_(app.gltable[1].description, 'first')

@with_app(app_txns_in_different_date_ranges)
def test_previous_balance_rows(app):
    # We show previous balance rows where appropriate
    app.drsel.select_next_date_range()
    eq_(app.gltable[1].description, 'Previous Balance')
    eq_(app.gltable[1].balance, '42.00')
    assert app.gltable.is_bold_row(1)

#---
def app_txn_in_income():
    app = TestApp()
    app.add_account('foo', account_type=AccountType.Income)
    app.add_account('bar')
    app.add_txn(description='hello', from_='foo', to='bar', amount='42')
    app.show_glview()
    return app

@with_app(app_txn_in_income)
def test_balance_cell_is_empty_for_income_entries(app):
    # Balance doesn't make any sense in income/expense, so don't show it
    row = app.gltable[4] # income account shown second
    eq_(row.balance, '')
