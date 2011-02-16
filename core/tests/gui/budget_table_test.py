# Created By: Virgil Dupras
# Created On: 2009-08-22
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...model.account import AccountType

def app_with_budget(monkeypatch):
    app = TestApp()
    monkeypatch.patch_today(2008, 1, 27)
    app.drsel.select_today_date_range()
    app.add_account('Some Expense', account_type=AccountType.Expense)
    app.add_budget('Some Expense', None, '100')
    app.mw.select_budget_table()
    return app

@with_app(app_with_budget)
def test_attrs(app):
    eq_(len(app.btable), 1)
    row = app.btable[0]
    eq_(row.start_date, '01/01/2008')
    eq_(row.stop_date, '')
    eq_(row.repeat_type, 'Monthly')
    eq_(row.interval, '1')
    eq_(row.account, 'Some Expense')
    eq_(row.target, '')
    eq_(row.amount, '100.00')

@with_app(app_with_budget)
def test_delete(app):
    # calling delete() deletes the selected rows
    app.btable.select([0])
    app.mw.delete_item()
    eq_(len(app.btable), 0)
    # And the spawns aren't there anymore in the ttable
    app.mw.select_transaction_table()
    eq_(app.ttable.row_count, 0)

@with_app(app_with_budget)
def test_edition_must_stop(app):
    # When the edition_must_stop event is broadcasted, btable must ignore it because the objc
    # side doesn't have a stop_editing method.
    app.clear_gui_calls()
    app.doc.stop_edition()
    app.btable_gui.check_gui_calls_partial(not_expected=['stop_editing'])

