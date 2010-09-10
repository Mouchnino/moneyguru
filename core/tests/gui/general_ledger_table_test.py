# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from ..base import TestApp, with_app

#---
def app_two_sided_txn():
    app = TestApp()
    app.add_accounts('foo', 'bar')
    app.add_txn(description='hello', from_='foo', to='bar', amount='42')
    app.show_glview()
    return app

@with_app(app_two_sided_txn)
def test_rows_data_with_two_sided_txn(app):
    # In a general ledger, we end up with 6 lines: 2 account lines (titles), two entry lines as well
    # as two total lines.
    eq_(len(app.gltable), 6)
    ACCOUNT_ROWS = {0, 3}
    BOLD_ROWS = {2, 5}
    for i in range(6):
        eq_(app.gltable.is_account_row(i), i in ACCOUNT_ROWS)
        eq_(app.gltable.is_bold_row(i), i in BOLD_ROWS)
    eq_(app.gltable[0].account_name, 'bar')
    eq_(app.gltable[3].account_name, 'foo')
    eq_(app.gltable[1].description, 'hello')
    eq_(app.gltable[1].debit, '42.00')
    eq_(app.gltable[4].description, 'hello')
    eq_(app.gltable[4].credit, '42.00')

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