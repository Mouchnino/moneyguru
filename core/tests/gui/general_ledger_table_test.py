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

