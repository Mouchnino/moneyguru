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

from .base import TestApp, with_app

def first_debit_credit_indexes(app):
    return (0, 1) if app.stable[0].debit else (1, 0)

#--- Simple Transaction
def app_simple_transaction():
    app = TestApp()
    app.add_txn('20/02/2010', from_='foo', to='bar', amount='42')
    app.tpanel.load()
    return app

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

#--- Transaction With Splits
def app_transaction_with_splits():
    app = TestApp()
    splits = [('foo', '', '37', ''), ('bar', '', '', '42'), ('baz', '', '5', '')]
    app.add_txn_with_splits(splits, date='20/02/2010')
    app.tpanel.load()
    return app

def test_change_split_create_new_unassigned():
    # Changing a split creates a new unassigned split.
    app = app_transaction_with_splits()
    app.stable[1].credit = '43'
    app.stable.save_edits()
    eq_(len(app.stable), 4)
    eq_(app.stable[3].account, '')
    eq_(app.stable[3].debit, '1.00')

def test_delete_split_creates_new_unassigned():
    # Deleting a split doesn't affect the txn amount. It recreates an unassigned split at stable's
    # bottom.
    app = app_transaction_with_splits()
    app.stable.select([1])
    app.stable.delete()
    eq_(app.stable[1].debit, '5.00')
    eq_(app.stable[2].credit, '42.00')

#--- Unassigned splits
def app_unassigned_splits():
    app = TestApp()
    splits = [('foo', '', '41', ''), ('bar', '', '', '42'), ('', '', '1', '')]
    app.add_txn_with_splits(splits, date='20/02/2010')
    app.tpanel.load()
    return app

@with_app(app_unassigned_splits)
def test_neutralizing_unassigned_split_removes_it(app):
    # When editing a split results in an unassigned split being put to 0, we remove it.
    app.stable[0].debit = '42' # The unsassigned split should end up being deleted.
    app.stable.save_edits()
    eq_(len(app.stable), 2)

#--- Unassigned main split
def app_unassigned_main_split():
    app = TestApp()
    app.add_txn('20/02/2010', from_='foo', to='', amount='42')
    # We have a transaction with one of the main splits being unassigned
    app.tpanel.load()
    return app

@with_app(app_unassigned_main_split)
def test_nullifying_unassigned_main_split_removes_it(app):
    # When an unassigned split because null, *even* if it's a main split, it's removed
    app.stable.add()
    app.stable[2].debit = '42'
    app.stable.save_edits()
    eq_(len(app.stable), 2)
