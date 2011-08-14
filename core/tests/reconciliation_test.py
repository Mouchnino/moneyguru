# Created By: Virgil Dupras
# Created On: 2008-05-28
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from .base import TestApp, with_app, compare_apps
from ..model.account import AccountType

#--- Pristine
@with_app(TestApp)
def test_reconciliation_mode(app):
    #Toggling reconciliation mode on and off
    app.clear_gui_calls()
    assert not app.aview.reconciliation_mode
    app.aview.toggle_reconciliation_mode()
    app.check_gui_calls(app.aview_gui, ['refresh_reconciliation_button'])
    assert app.aview.reconciliation_mode
    app.aview.toggle_reconciliation_mode()
    assert not app.aview.reconciliation_mode

#--- One account
def app_one_account():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    return app

@with_app(app_one_account)
def test_multiple_recdate_overlapping(app):
    # Oven invalidations take place correctly even when there are multiple overlapping in dates and
    # reconciliation dates. That's a tricky one.
    # Here we have 4 entries, a first one overlapping the 2nd, and the second overlapping the third.
    # then, we have a 4th entry with a date and recdate equal to the recdate of the last. When we
    # reconcile the last entry, the oven must correctly chain invalidations to go up to the first
    # one.
    app.aview.toggle_reconciliation_mode()
    app.add_entry('03/08/2010', increase='1', reconciliation_date='06/08/2010')
    app.add_entry('04/08/2010', increase='2', reconciliation_date='07/08/2010')
    app.add_entry('05/08/2010', increase='4', reconciliation_date='05/08/2010')
    app.add_entry('07/08/2010', increase='8')
    # We do the last one in two steps because otherwise, we are over-invalidated by the add_entry
    # operation, causing the test to incorrectly pass.
    app.etable[3].toggle_reconciled()
    eq_(app.etable[3].balance, '15.00')

#--- One entry
def app_one_entry():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('11/07/2008', decrease='42')
    return app

@with_app(app_one_entry)
def test_disallow_reconciliation_date_lower_than_entry_date(app):
    # Reconciliation dates that are lower than entry dates don't make any sense and are the cause
    # of bugs in the reconciliation balance counting mechanism. Don't allow that.
    app.etable[0].reconciliation_date = '10/07/2008'
    app.etable.save_edits()
    eq_(app.etable[0].reconciliation_date, '11/07/2008')
    # Also adjust recdate if tdate changes
    app.etable[0].date = '12/07/2008'
    app.etable.save_edits()
    eq_(app.etable[0].reconciliation_date, '12/07/2008')

@with_app(app_one_entry)
def test_initial_attrs(app):
    # initially, an entry is not reconciled
    assert not app.etable[0].reconciled
    eq_(app.etable[0].reconciliation_date, '')

@with_app(app_one_entry)
def test_set_reconciliation_date(app):
    # It's possible to set any date as a reconciliation date (even when not in reconciliation
    # mode).
    app.etable[0].reconciliation_date = '12/07/2008'
    app.etable.save_edits()
    eq_(app.etable[0].reconciliation_date, '12/07/2008')

@with_app(app_one_entry)
def test_toggle_entries_reconciled(app):
    # When reconciliation mode is off, doesn't do anything.
    app.etable.toggle_reconciled()
    assert not app.etable[0].reconciled

#--- One entry in reconciliation mode
def app_one_entry_reconciliation_mode():
    app = TestApp()    
    app.add_account()
    app.mw.show_account()
    app.add_entry('11/07/2008', decrease='42')
    app.aview.toggle_reconciliation_mode()
    return app

@with_app(app_one_entry_reconciliation_mode)
def test_can_reconcile_entry(app):
    # An entry today is reconciliable.
    assert not app.etable[0].reconciled
    assert app.etable[0].can_reconcile()

@with_app(app_one_entry_reconciliation_mode)
def test_cant_reconcile_previous_balance_entry(app):
    # It's not possible to reconcile a previous balance entry.
    app.drsel.select_next_date_range()
    # The first entry is not a "Previous Balance" entry
    assert not app.etable[0].can_reconcile()

@with_app(app_one_entry_reconciliation_mode)
def test_commit_reconciliation(app):
    # committing reconciliation sets the entry's reconciliation date to the txn's date
    app.etable.selected_row.toggle_reconciled()
    app.aview.toggle_reconciliation_mode()
    assert app.etable[0].reconciled
    eq_(app.etable[0].reconciliation_date, '11/07/2008')

@with_app(app_one_entry_reconciliation_mode)
def test_reconciling_sets_dirty_flag(app):
    # Reconciling an entry sets the dirty flag.
    app.save_file()
    app.etable.selected_row.toggle_reconciled()
    assert app.doc.is_dirty()

@with_app(app_one_entry_reconciliation_mode)
def test_reconciliation_balance(app):
    # Unreconcilied entries return a None balance, and reconciled entries return a 
    # reconciliation balance
    eq_(app.etable[0].balance, '')
    row = app.etable.selected_row
    row.toggle_reconciled()
    eq_(app.etable[0].balance, '-42.00')

@with_app(app_one_entry_reconciliation_mode)
def test_toggle_reconciled(app):
    # calling toggle_reconciled() on a row toggles reconciliation and shows a reconciliation
    # balance.
    app.etable.selected_row.toggle_reconciled()
    assert app.etable[0].reconciled
    eq_(app.etable[0].balance, '-42.00')

@with_app(app_one_entry_reconciliation_mode)
def test_toggle_entries_reconciled_sets_dirty_flag(app):
    # Toggling reconciliation sets the dirty flag.
    app.save_file()
    app.etable.toggle_reconciled()
    assert app.doc.is_dirty()

#--- Entry in future
def app_entry_in_future(monkeypatch):
    monkeypatch.patch_today(2009, 12, 26)
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('27/12/2009', increase='42')
    app.aview.toggle_reconciliation_mode()
    return app

@with_app(app_entry_in_future)
def test_can_reconcile_entry_in_future(app):
    # It's not possible to reconcile an entry in the future.
    assert not app.etable[0].can_reconcile()

#--- Entry in liability
def app_entry_in_liability():
    app = TestApp()
    app.add_account(account_type=AccountType.Liability)
    app.mw.show_account()
    app.add_entry(increase='42')
    app.aview.toggle_reconciliation_mode()
    return app

@with_app(app_entry_in_liability)
def test_entry_balance_in_liability(app):
    # The balance of the entry is empty.
    # Previously, it would crash because it would try to negate None
    eq_(app.etable[0].balance, '')

#--- Reconciled entry
def app_reconciled_entry():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('11/07/2008', transfer='foo', decrease='42')
    app.aview.toggle_reconciliation_mode()
    app.etable.selected_row.toggle_reconciled()
    app.aview.toggle_reconciliation_mode()
    return app

@with_app(app_reconciled_entry)
def test_change_amount_currency_dereconciles_entry(app):
    # Changing an antry's amount to another currency de-reconciles it.
    app.etable[0].decrease = '12eur'
    app.etable.save_edits()
    assert not app.etable[0].reconciled

@with_app(app_reconciled_entry)
def test_change_amount_currency_from_other_side_dereconciles_entry(app):
    # Changing an entry's amount from the "other side" also de-reconcile that entry
    app.mainwindow.show_account()
    app.etable[0].increase = '12eur'
    app.etable.save_edits()
    app.mainwindow.show_account()
    assert not app.etable[0].reconciled

@with_app(app_reconciled_entry)
def test_change_date_makes_reconciliation_date_follow(app):
    # Changing the date of an entry makes the reconciliation date follow. This is to make sure that
    # people not using the reconciliation date field will not end up with date != recdate.
    app.etable[0].date = '10/07/2008'
    app.etable.save_edits()
    eq_(app.etable[0].reconciliation_date, '10/07/2008')

@with_app(app_reconciled_entry)
def test_change_ttable_expense_account_doesnt_unreconcile_entry(app):
    # Changing the expense account of a txn for which the asset side is reconciled doesn't
    # unreconcile it.
    app.show_tview()
    app.ttable[0].to = 'other_expense'
    app.ttable.save_edits()
    assert app.ttable[0].reconciled

@with_app(app_reconciled_entry)
def test_change_ttable_asset_account_unreconciles_entry(app):
    # Changing the account of a txn for which the entry is reconciled unreconciles it.
    app.show_tview()
    app.ttable[0].from_ = 'other_asset'
    app.ttable.save_edits()
    assert not app.ttable[0].reconciled

#--- Entry different reconciliation date
def app_entry_different_reconciliation_date(monkeypatch):
    app = TestApp()
    monkeypatch.patch_today(2008, 7, 20)
    app.add_account()
    app.mw.show_account()
    app.add_entry('11/07/2008', decrease='42')
    app.etable[0].reconciliation_date = '12/07/2008'
    app.etable.save_edits()
    return app

@with_app(app_entry_different_reconciliation_date)
def test_save_and_load_different_reconciliation_date(app):
    # reconciliation date is correctly saved and loaded
    newapp = app.save_and_load()
    newapp.bsheet.selected = newapp.bsheet.assets[0]
    newapp.mw.show_account()
    eq_(newapp.etable[0].reconciliation_date, '12/07/2008')

#--- Three entries
def app_three_entries():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('1/1/2008', 'one')
    app.add_entry('20/1/2008', 'two')
    app.add_entry('31/1/2008', 'three')
    app.aview.toggle_reconciliation_mode()
    return app

@with_app(app_three_entries)
def test_reconcile_not_selected(app):
    # Reconciling also selects the entry.
    # current selection is the last entry.
    app.etable[0].toggle_reconciled()
    eq_(app.etable.selected_index, 0)

@with_app(app_three_entries)
def test_toggle_reconcile_then_save(app):
    # saving the file commits reconciliation
    app.etable[1].toggle_reconciled()
    app.save_file()
    assert app.etable[1].reconciled

#--- Three entries one reconciled
def app_three_entries_one_reconciled():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('1/1/2008', 'one', increase='1')
    app.add_entry('20/1/2008', 'two', increase='2')
    app.add_entry('31/1/2008', 'three', increase='3')
    app.aview.toggle_reconciliation_mode()
    app.etable.select([1])
    app.etable.selected_row.toggle_reconciled()
    return app

@with_app(app_three_entries_one_reconciled)
def test_save_load_with_one_reconciled_entry(app):
    newapp = app.save_and_load()
    newapp.doc.date_range = app.doc.date_range
    newapp.doc._cook()
    compare_apps(app.doc, newapp.doc)

@with_app(app_three_entries_one_reconciled)
def test_toggle_entries_reconciled_with_none_reconciled(app):
    # When none of the selected entries are reconciled, all selected entries get reconciled.
    app.etable.select([0, 2])
    app.etable.toggle_reconciled()
    assert app.etable[0].reconciled
    assert app.etable[2].reconciled

@with_app(app_three_entries_one_reconciled)
def test_toggle_entries_reconciled_with_all_reconciled(app):
    # When all of the selected entries are reconciled, all selected entries get de-reconciled
    app.etable.select([0, 2])
    app.etable.toggle_reconciled() # Both reconciled now
    app.etable.toggle_reconciled()
    assert not app.etable[0].reconciled
    assert not app.etable[2].reconciled

@with_app(app_three_entries_one_reconciled)
def test_toggle_entries_reconciled_with_some_reconciled(app):
    # When some of the selected entries are reconciled, all selected entries get reconciled
    app.etable.select([0, 1, 2]) # entry at index 1 is pending reconciliation
    app.etable.toggle_reconciled()
    assert app.etable[0].reconciled
    assert app.etable[1].reconciled
    assert app.etable[2].reconciled

@with_app(app_three_entries_one_reconciled)
def test_set_txn_date_in_the_future(app, monkeypatch):
    # Setting a reconciled txn's date in the future de-reconciles it.
    monkeypatch.patch_today(2008, 2, 1)
    app.etable[1].date = '02/02/2008'
    app.etable.save_edits()
    # Our txn is now the last one, so we test index 2
    assert not app.etable[2].reconciled

@with_app(app_three_entries_one_reconciled)
def test_cant_change_account_currency(app):
    # We cannot change an account currency if this account has reconciled entries.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.mw.edit_item()
    assert not app.apanel.can_change_currency

@with_app(app_three_entries_one_reconciled)
def test_can_change_other_account_attributes(app):
    # There was a bug causing any attribute change through apanel to throw an assertion error.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.mw.edit_item()
    app.apanel.notes = 'foo'
    app.apanel.save() # no crash

#--- Three entries all reconciled
def app_three_entries_all_reconciled():
    app = TestApp()
    app.add_account('account')
    app.mw.show_account()
    app.add_entry('1/1/2008', 'one', increase='1', reconciliation_date='1/1/2008')
    app.add_entry('2/1/2008', 'two', increase='2', reconciliation_date='2/1/2008')
    app.add_entry('3/1/2008', 'three', increase='4', reconciliation_date='3/1/2008')
    return app

@with_app(app_three_entries_all_reconciled)
def test_reconcile_schedule_spawn_by_setting_recdate(app):
    # When the user only changes the reconciliation date of a spawn, don't ask for scope and
    # correctly materialize the spawn.
    app.add_schedule(start_date='4/1/2008', account='account', amount='8', repeat_every=10)
    app.show_account('account')
    app.aview.toggle_reconciliation_mode()
    app.etable[3].reconciliation_date = '4/1/2008'
    app.etable.save_edits()
    app.check_gui_calls_partial(app.doc_gui, not_expected=['query_for_schedule_scope'])
    assert not app.etable[3].recurrent
    # There was a bug that caused the spawn to be duplicated when setting a reconciliation date for it.
    assert not app.etable[4].reconciled

#--- Entries with a different order under reconciliation date sorting
def app_different_reconciliation_date_order():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    # when sorting by reconciliation date, 'two' comes first.
    app.add_entry('19/1/2008', 'one', increase='1', reconciliation_date='22/1/2008')
    app.add_entry('20/1/2008', 'two', increase='2', reconciliation_date='20/1/2008')
    app.add_entry('23/1/2008', 'three', increase='3')
    app.aview.toggle_reconciliation_mode()
    return app

@with_app(app_different_reconciliation_date_order)
def test_reconciling_third_entry_makes_the_oven_start_off_with_correct_entry_as_base(app):
    app.etable.select([2])
    app.etable.toggle_reconciled()
    eq_(app.etable[2].balance, '6.00')

@with_app(app_different_reconciliation_date_order)
def test_reconciliation_balance_is_determined_by_reconciliation_date(app):
    # The order in which balances are computed in reconciliation mode is determined by entries'
    # reconciliation date, not base date.
    eq_(app.etable[0].balance, '3.00')
    eq_(app.etable[1].balance, '2.00')

@with_app(app_different_reconciliation_date_order)
def test_toggle_reconciliation_of_second(app):
    # toggling the reconciliation of the second entry invalidates cooked data of the first one, even
    # if its date is before the second entry's date
    app.etable[1].toggle_reconciled()
    eq_(app.etable[0].balance, '1.00')

@with_app(app_three_entries_one_reconciled)
def test_set_reconciliation_date_lower_than_other(app):
    # When setting a reconciliation date lower than others', be sure to recook others
    app.etable[0].reconciliation_date = '19/1/2008' # lower than 'two'
    app.etable.save_edits()
    eq_(app.etable[1].balance, '3.00')
    # then, when setting it to a later date, update the second entry as well
    app.etable[0].reconciliation_date = '32/1/2008'
    app.etable.save_edits()
    eq_(app.etable[1].balance, '2.00')

#---
def app_entries_linked_to_same_txn_and_same_account():
    app = TestApp()
    app.add_account('foo')
    app.add_txn('14/09/2010', from_='foo', to='foo', amount='42')
    app.add_txn('15/09/2010', from_='bar', to='foo', amount='10')
    app.show_account('foo')
    return app

@with_app(app_entries_linked_to_same_txn_and_same_account)
def test_reconcile_all(app):
    # When having two entries linked to the same account in the same transaction, pick the correct
    # split to resume balance calculations
    app.aview.toggle_reconciliation_mode()
    app.etable.select([0, 1])
    app.etable.toggle_reconciled()
    app.etable.select([2])
    app.etable.toggle_reconciled()
    # Previously, the first entry would be used as a base to resume the computations instead of the
    # second.
    eq_(app.etable[2].balance, '10.00')
