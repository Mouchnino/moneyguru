# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...gui.transaction_print import EntryPrint

#--- Some account
def app_with_account():
    app = TestApp()
    app.add_account('foobar')
    app.show_account()
    app.pv = EntryPrint(app.aview)
    return app

@with_app(app_with_account)
def test_title(app):
    # In the EntryView, the title is in two lines, the first line being the account name
    assert app.pv.title.startswith('foobar\n')

#--- Split transaction
def app_split_transaction():
    app = TestApp()
    splits = [
        ('foo', 'foo memo', '100', ''),
        ('bar', '', '', '100'),
        ('split1', 'some memo', '10', ''),
        ('split2', '', '', '1'),
        ('', '', '', '9'),
    ]
    app.add_txn_with_splits(splits)
    app.add_txn(from_='foo', to='bar', amount='42')
    app.show_account()
    app.pv = EntryPrint(app.aview)
    return app

@with_app(app_split_transaction)
def test_split_count(app):
    # We show all splits, even the 'main' one (to make sure we print all memos)
    eq_(app.pv.split_count_at_row(0), 5)
    eq_(app.pv.split_count_at_row(1), 2)

@with_app(app_split_transaction)
def test_split_values(app):
    eq_(app.pv.split_values(0, 0), ['foo', 'foo memo', '100.00'])
    eq_(app.pv.split_values(0, 2), ['split1', 'some memo', '10.00'])
    eq_(app.pv.split_values(0, 4), ['Unassigned', '', '-9.00'])

@with_app(app_split_transaction)
def test_main_split_always_first(app):
    # Always show the "main" split (the one represented by the entry) first.
    aview = app.show_account('bar')
    pv = EntryPrint(aview)
    eq_(pv.split_values(0, 0), ['bar', '', '-100.00'])

#--- Entry in previous range
def app_entry_in_previous_range():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account()
    app.show_account()
    app.add_entry('1/1/2008')
    app.drsel.select_next_date_range()
    app.pv = EntryPrint(app.aview)
    return app

@with_app(app_entry_in_previous_range)    
def test_split_count_of_previous_balance_entry(app):
    # For the "Previous Balance" entry, return 0, don't crash
    eq_(app.pv.split_count_at_row(0), 0)
