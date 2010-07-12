# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from ..base import TestApp, with_app
from ...gui.entry_print import EntryPrint

#--- Split transaction
def app_split_transaction():
    app = TestApp()
    splits = [
        ('foo', '', '100', ''),
        ('bar', '', '', '100'),
        ('split1', 'some memo', '10', ''),
        ('split2', '', '', '1'),
        ('', '', '', '9'),
    ]
    app.add_txn_with_splits(splits)
    app.add_txn(from_='foo', to='bar', amount='42')
    app.mw.show_account()
    app.pv = EntryPrint(app.etable)
    return app

@with_app(app_split_transaction)
def test_split_count(app):
    eq_(app.pv.split_count_at_row(0), 4)
    eq_(app.pv.split_count_at_row(1), 1)

@with_app(app_split_transaction)
def test_split_values(app):
    eq_(app.pv.split_values(0, 1), ['split1', 'some memo', '10.00'])
    eq_(app.pv.split_values(0, 3), ['Unassigned', '', '-9.00'])

#--- Entry in previous range
def app_entry_in_previous_range():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account()
    app.mw.show_account()
    app.add_entry('1/1/2008')
    app.drsel.select_next_date_range()
    app.pv = EntryPrint(app.etable)
    return app

@with_app(app_entry_in_previous_range)    
def test_split_count_of_previous_balance_entry(app):
    # For the "Previous Balance" entry, return 0, don't crash
    eq_(app.pv.split_count_at_row(0), 0)
