# Created By: Virgil Dupras
# Created On: 2010-01-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_, patch_today

from ...model.account import AccountType
from ..base import TestApp, with_app

#--- Transactions with info filled up
# Transactions with all kinds of info filled up (desc, payee, checkno...)
def app_transactions_with_info_filled_up():
    app = TestApp()
    app.add_txn(date='30/11/2009', description='desc', payee='payee', checkno='123', from_='from',
        to='to', amount='42')
    app.add_txn(date='01/12/2009', description='aaa', payee='zzz', checkno='321', from_='aaa',
        to='zzz', amount='41')
    app.add_txn(date='02/12/2009', description='zzz', payee='aaa', checkno='000', from_='zzz',
        to='aaa', amount='43')
    return app

@with_app(app_transactions_with_info_filled_up)
def test_sort_by_date(app):
    # Sorting by date use the datetime value for sorting, not the string value.
    app.ttable.sort_by('date')
    eq_(app.ttable[0].date, '30/11/2009')
    eq_(app.ttable[1].date, '01/12/2009')
    eq_(app.ttable[2].date, '02/12/2009')

@with_app(app_transactions_with_info_filled_up)
def test_sort_by_description(app):
    # Sorting by description works
    app.ttable.sort_by('description')
    eq_(app.ttable[0].description, 'aaa')
    eq_(app.ttable[1].description, 'desc')
    eq_(app.ttable[2].description, 'zzz')

@with_app(app_transactions_with_info_filled_up)
def test_sort_by_description_desc(app):
    # When `desc` is True, the sort order is inverted
    app.ttable.sort_by('description', desc=True)
    eq_(app.ttable[0].description, 'zzz')
    eq_(app.ttable[1].description, 'desc')
    eq_(app.ttable[2].description, 'aaa')

@with_app(app_transactions_with_info_filled_up)
def test_sort_by_from(app):
    # we deal with the from --> from_ escaping. At the time this test was written, it didn't
    # fail because the we're just fetching '_from', but it's still a case that can very likely
    # fail in future re-factorings.
    app.ttable.sort_by('from')
    eq_(app.ttable[0].from_, 'aaa')
    eq_(app.ttable[1].from_, 'from')
    eq_(app.ttable[2].from_, 'zzz')

@with_app(app_transactions_with_info_filled_up)
def test_sort_preserves_total_row(app):
    # When sorting, the total row stays where it is, at the bottom of the table. We test it on
    # etable because at the time the test was created, it wasn't added to ttable yet.
    app.show_account('from') # There's now only one entry and the total row.
    app.etable.sort_by('description')
    eq_(app.etable[1].description, 'TOTAL')

#--- Transactions with accents
# Transactions with accented letters in their descriptions
def app_transactions_with_accents():
    app = TestApp()
    app.add_txn(description='aaa')
    app.add_txn(description='ZZZ')
    app.add_txn(description='ez')
    app.add_txn(description='éa')
    return app

@with_app(app_transactions_with_accents)
def test_sort_by_description_considers_accents(app):
    # Letters with accents are treated as if they didn't have their accent.
    app.ttable.sort_by('description')
    eq_(app.ttable[0].description, 'aaa')
    eq_(app.ttable[1].description, 'éa')
    eq_(app.ttable[2].description, 'ez')
    eq_(app.ttable[3].description, 'ZZZ')

#--- Entries with reconciliation date
def app_entries_with_reconciliation_date():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('05/01/2010')
    app.add_entry('05/01/2010')
    app.etable[1].reconciliation_date = '05/01/2010'
    app.etable.save_edits()
    return app

@with_app(app_entries_with_reconciliation_date)
def test_sort_by_reconciliation_date(app):
    # Don't crash because some dates are None.
    app.etable.sort_by('reconciliation_date') # no crash
    eq_(app.etable[0].reconciliation_date, '05/01/2010')
    eq_(app.etable[1].reconciliation_date, '')

#--- Two budgets with one stop date
def app_two_budgets_one_stop_date():
    app = TestApp()
    app.add_account('expense', account_type=AccountType.Expense)
    app.add_budget('expense', None, '42', stop_date=None)
    app.add_budget('expense', None, '42', stop_date='21/12/2012')
    return app

@with_app(app_two_budgets_one_stop_date)
def test_sort_btable_by_stop_date(app):
    # Don't crash because some dates are None.
    app.btable.sort_by('stop_date') # no crash
    eq_(app.btable[0].stop_date, '')
    eq_(app.btable[1].stop_date, '21/12/2012')

#--- Two schedules one stop date
def app_two_schedules_one_stop_date():
    app = TestApp()
    app.add_schedule(stop_date=None)
    app.add_schedule(stop_date='21/12/2012')
    return app

@with_app(app_two_schedules_one_stop_date)
def test_sort_sctable_by_stop_date(app):
    # Don't crash because some dates are None.
    app.sctable.sort_by('stop_date') # no crash
    eq_(app.sctable[0].stop_date, '')
    eq_(app.sctable[1].stop_date, '21/12/2012')

#--- Two transactions different currencies
def app_two_txn_different_currencies():
    app = TestApp()
    app.add_txn(amount='42 GBP')
    app.add_txn(amount='43 CAD')
    return app

@with_app(app_two_txn_different_currencies)
def test_sort_by_amount(app):
    # When sorting by amount, just use the raw number as a sort key. Ignore currencies.
    app.ttable.sort_by('amount') # no crash
    eq_(app.ttable[0].amount, 'GBP 42.00')
    eq_(app.ttable[1].amount, 'CAD 43.00')

#--- Mixed up reconciled schedule and budget
# A mix of 4 txns. One reconciled, one normal, one schedule spawn and one budget spawn.
def app_mixed_up_schedule_and_budget(monkeypatch):
    patch_today(monkeypatch, 2010, 1, 1)
    app = TestApp()
    app.drsel.select_month_range() # we just want 4 transactions
    app.add_account('expense', account_type=AccountType.Expense)
    app.add_account('asset')
    app.mw.show_account()
    app.add_entry('02/01/2010', description='reconciled')
    app.etable[0].reconciliation_date = '02/01/2010'
    app.etable.save_edits()
    app.add_txn('01/01/2010', description='plain', from_='asset')
    app.add_schedule(repeat_type_index=2, description='schedule', account='asset', amount='42') # monthly
    app.add_budget('expense', 'asset', '500', start_date='01/01/2010')
    return app

@with_app(app_mixed_up_schedule_and_budget)
def test_sort_etable_by_status(app):
    # Reconciled are first, then plain, then schedules, then budgets
    app.mw.select_entry_table() # 'asset' is already selected from setup
    app.etable.sort_by('status')
    eq_(app.etable[0].description, 'reconciled')
    eq_(app.etable[1].description, 'plain')
    eq_(app.etable[2].description, 'schedule')
    assert app.etable[3].is_budget

@with_app(app_mixed_up_schedule_and_budget)
def test_sort_ttable_by_status(app):
    # Reconciled are first, then plain, then schedules, then budgets
    app.mw.select_transaction_table()
    app.ttable.sort_by('status')
    eq_(app.ttable[0].description, 'reconciled')
    eq_(app.ttable[1].description, 'plain')
    eq_(app.ttable[2].description, 'schedule')
    assert app.ttable[3].is_budget

#--- Two transactions added when sorted by description
def app_two_txns_added_when_sorted_by_description():
    app = TestApp()
    app.mw.select_transaction_table()
    app.ttable.sort_by('description')
    app.add_txn(description='foo', from_='asset')
    app.add_txn(description='bar', from_='asset')
    return app

@with_app(app_two_txns_added_when_sorted_by_description)
def test_can_move_etable_row(app):
    # a row in etable can only be moved when the sort descriptor is ('date', False)
    app.show_account('asset')
    app.etable.sort_by('description')
    assert not app.etable.can_move([1], 0)
    app.etable.sort_by('date')
    assert app.etable.can_move([1], 0)

@with_app(app_two_txns_added_when_sorted_by_description)
def test_can_move_ttable_row(app):
    # a row in ttable can only be moved when the sort descriptor is ('date', False)
    assert not app.ttable.can_move([1], 0)
    app.ttable.sort_by('date')
    assert app.ttable.can_move([1], 0)

@with_app(app_two_txns_added_when_sorted_by_description)
def test_sort_etable_by_description_then_by_date(app):
    # Like with ttable, etable doesn't ignore txn position when sorting by date.
    app.show_account('asset')
    app.etable.sort_by('description')
    app.etable.sort_by('date')
    eq_(app.etable[0].description, 'foo')
    eq_(app.etable[1].description, 'bar')

@with_app(app_two_txns_added_when_sorted_by_description)
def test_sort_ttable_by_date(app):
    # When sorting by date, the "position" attribute of the transaction is taken into account
    # when transactions have the same date.
    app.ttable.sort_by('date')
    eq_(app.ttable[0].description, 'foo')
    eq_(app.ttable[1].description, 'bar')

@with_app(app_two_txns_added_when_sorted_by_description)
def test_sort_order_persistent(app):
    # When changing transactions, the table is re-sorted automatically according to the current
    # sorting.
    eq_(app.ttable[0].description, 'bar')
    eq_(app.ttable[1].description, 'foo')
