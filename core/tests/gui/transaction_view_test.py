# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_
from hscommon.currency import USD

from ..base import TestApp, with_app

#--- three transactions
def app_three_transactions():
    app = TestApp()
    app.add_txn(amount='1')
    app.add_txn(amount='2')
    app.add_txn(amount='3')
    return app

@with_app(app_three_transactions)
def test_totals_select_one(app):
    # the totals line shows the number of selected transactions
    expected = "1 out of 3 selected. Amount: 3.00"
    eq_(app.mw.status_line, expected)

@with_app(app_three_transactions)
def test_totals_select_two(app):
    # when two transactions are selected, the totals line changes
    app.ttable.select([1, 2])
    expected = "2 out of 3 selected. Amount: 5.00"
    eq_(app.mw.status_line, expected)

#--- Multiple currencies
def app_multiple_currencies():
    app = TestApp()
    USD.set_CAD_value(2, date(2010, 3, 9))
    app.add_txn('10/03/2010', amount='10')
    app.add_txn('10/03/2010', amount='10 CAD') # worth 5usd
    return app

@with_app(app_multiple_currencies)
def test_totals_select_all(app):
    # Foreign amounts are converted
    app.ttable.select([0, 1])
    expected = "2 out of 2 selected. Amount: 15.00"
    eq_(app.mw.status_line, expected)
