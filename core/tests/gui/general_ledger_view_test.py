# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hsutil.testutil import eq_

from ...model.account import AccountType
from ..base import TestApp, with_app

#---
def app_two_txns():
    app = TestApp()
    app.add_account('one')
    app.add_account('two', account_type=AccountType.Liability)
    app.add_txn(description='first', from_='one', to='two', amount='42')
    app.add_txn(description='second', from_='two', to='one', amount='12')
    app.show_glview()
    return app

@with_app(app_two_txns)
def test_totals_one_selected(app):
    # the totals line shows totals for selected entries
    print(len(app.gltable))
    app.gltable.select([1])
    expected = "1 out of 4 selected. Debit: 0.00 Credit: 42.00"
    eq_(app.mw.status_line, expected)

@with_app(app_two_txns)
def test_totals_four_selected(app):
    # the totals line shows totals for selected entries
    app.gltable.select([1, 2, 5, 6])
    expected = "4 out of 4 selected. Debit: 54.00 Credit: 54.00"
    eq_(app.mw.status_line, expected)
