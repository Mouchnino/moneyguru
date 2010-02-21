# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-20
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_
from hsutil.currency import USD

from .base import TestApp

def first_debit_credit(app):
    # The order of the splits is not defined, so we test whatever split has a debit
    debit = app.stable[0].debit or app.stable[1].debit
    credit = app.stable[0].credit or app.stable[1].credit
    return debit, credit

def first_debit_credit_indexes(app):
    return (0, 1) if app.stable[0].debit else (1, 0)

#--- Amountless Transaction
def app_amountless_transaction():
    app = TestApp()
    app.add_txn('20/02/2010')
    app.tpanel.load()
    return app

def test_change_split_amount():
    # Changing the split amount in a transaction with a 0 amount will change the transaction amount
    app = app_amountless_transaction()
    app.stable[0].credit = '43'
    app.stable.save_edits()
    eq_(app.tpanel.amount, '43.00')
    eq_(len(app.stable), 2)

#--- Simple Transaction
def app_simple_transaction():
    app = TestApp()
    app.add_txn('20/02/2010', from_='foo', to='bar', amount='42')
    app.tpanel.load()
    return app

def test_add_split_adjusts_main_splits():
    # Adding a split preserves the current txn amount
    app = app_simple_transaction()
    app.stable.add()
    app.stable[2].debit = '1'
    app.stable.save_edits()
    debit, credit = first_debit_credit(app)
    eq_(debit, '41.00')
    eq_(credit, '42.00')

def test_change_amount_currency():
    # Setting an amount of a different currency in the Amount field changes all splits' currency.
    app = app_simple_transaction()
    app.tpanel.amount = '12pln'
    eq_(app.tpanel.amount, 'PLN 12.00')
    debit, credit = first_debit_credit(app)
    eq_(debit, 'PLN 12.00')
    eq_(credit, 'PLN 12.00')

def test_reverse_main_split():
    # Reversing (changing it from debit to credit or vice versa) a main split reverses the other
    # main split.
    app = app_simple_transaction()
    dindex, cindex = first_debit_credit_indexes(app)
    app.stable[cindex].debit = '42'
    app.stable.save_edits()
    eq_(len(app.stable), 2)
    eq_(app.stable[cindex].debit, '42.00')
    eq_(app.stable[dindex].credit, '42.00')

def test_set_negative_amount():
    # When a negative amount is specified, we simply reverse it.
    app = app_simple_transaction()
    app.tpanel.amount = '-12'
    eq_(app.tpanel.amount, '12.00')

#--- Transaction With Splits
def app_transaction_with_splits():
    app = TestApp()
    app.add_txn('20/02/2010', from_='foo', to='bar', amount='42')
    app.tpanel.load()
    app.stable.add()
    app.stable[2].debit = '5'
    app.stable.save_edits()
    return app

def test_change_main_split():
    # Changing a main split changes the transaction amount
    app = app_transaction_with_splits()
    dindex, cindex = first_debit_credit_indexes(app)
    app.stable[cindex].credit = '43'
    app.stable.save_edits()
    eq_(app.tpanel.amount, '43.00')
    eq_(len(app.stable), 3)
    eq_(app.stable[dindex].debit, '38.00')

def test_set_amount():
    # Setting the amount of the txn adjusts the main splits.
    app = app_transaction_with_splits()
    app.tpanel.amount = '43'
    debit, credit = first_debit_credit(app)
    eq_(debit, '38.00')
    eq_(credit, '43.00')

#--- Multi-Currency Transaction
def app_multi_currency_transaction():
    app = TestApp()
    USD.set_CAD_value(0.8, date(2008, 1, 1))
    app.add_txn('20/02/2010')
    app.tpanel.load()
    app.stable[0].credit = '44 usd'
    app.stable.save_edits()
    app.stable.select([1])
    app.stable[1].debit = '42 cad'
    app.stable.save_edits()
    return app

def test_amount():
    # The amount of a multi-currency transaction is a conversion to native currency of all splits.
    app = app_multi_currency_transaction()
    # (44 + (42 / .8)) / 2
    eq_(app.tpanel.amount, '48.25')
