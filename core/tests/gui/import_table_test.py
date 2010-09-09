# Created By: Virgil Dupras
# Created On: 2008-08-08
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date
from hsutil.testutil import eq_

from ..base import TestApp, with_app, TestData
from ...model.date import YearRange

#---
def app_import_checkbook_qif():
    app = TestApp()
    app.doc.date_range = YearRange(date(2007, 1, 1))
    # The cocoa side does some disconnect/connect stuff. We have to refreshthe table on connect()
    app.itable.disconnect()
    app.doc.parse_file_for_import(TestData.filepath('qif', 'checkbook.qif'))
    app.itable.connect()
    app.clear_gui_calls()
    return app

@with_app(app_import_checkbook_qif)
def test_delete_is_linked_to_will_import(app):
    # calling delete() (the std API for all tables), set "will_import" to False
    app.itable.select([3, 4])
    app.itable.delete()
    assert not app.itable[3].will_import
    assert not app.itable[4].will_import

@with_app(app_import_checkbook_qif)
def test_is_two_sided_without_target_account(app):
    # There is no target account, we only have one side
    assert not app.itable.is_two_sided

@with_app(app_import_checkbook_qif)
def test_rows_after_checkbook_import(app):
    # The shown rows are the imported txns from the first account. The target account is a new 
    # file, so we don't have any 'left side' entries.
    eq_(len(app.itable), 5)
    eq_(app.itable[0].date, '')
    eq_(app.itable[0].description, '')
    eq_(app.itable[0].amount, '')
    eq_(app.itable[0].date_import, '01/01/2007')
    eq_(app.itable[0].description_import, 'Starting Balance')
    eq_(app.itable[0].amount_import, '42.32')
    eq_(app.itable[0].bound, False)
    assert app.itable[0].will_import
    assert app.itable[0].can_edit_will_import
    eq_(app.itable[1].transfer_import, 'Salary') # not all entries have a transfer
    eq_(app.itable[3].checkno_import, '36') # not all entries have a checkno
    eq_(app.itable[4].date, '')
    eq_(app.itable[4].description, '')
    eq_(app.itable[4].amount, '')
    eq_(app.itable[4].date_import, '04/02/2007')
    eq_(app.itable[4].description_import, 'Transfer')
    eq_(app.itable[4].payee_import, 'Account 2')
    eq_(app.itable[4].amount_import, '80.00')
    eq_(app.itable[4].bound, False)
    assert app.itable[4].will_import
    assert app.itable[4].can_edit_will_import

@with_app(app_import_checkbook_qif)
def test_select_account_pane_refreshes_table(app):
    # Selecting another accounts updates the table.
    app.iwin.selected_pane_index = 1
    app.check_gui_calls(app.itable_gui, ['refresh'])
    eq_(len(app.itable), 3)
    eq_(app.itable[1].date, '')
    eq_(app.itable[1].description, '')
    eq_(app.itable[1].amount, '')
    eq_(app.itable[1].date_import, '05/01/2007')
    eq_(app.itable[1].description_import, 'Interest')
    eq_(app.itable[1].amount_import, '8.92')
    eq_(app.itable[1].bound, False)

@with_app(app_import_checkbook_qif)
def test_toggle_import_status(app):
    # It's possible to toggle the import status of all selected rows at once.
    app.itable.select([1, 2, 3])
    app.itable.toggle_import_status()
    assert not app.itable[1].will_import
    assert not app.itable[2].will_import
    assert not app.itable[3].will_import
    app.check_gui_calls(app.itable_gui, ['refresh'])

@with_app(app_import_checkbook_qif)
def test_will_import_value_is_kept(app):
    # When changing the selected pane around, the will_import values are kept
    app.itable[4].will_import = False
    app.iwin.selected_pane_index = 1
    app.iwin.selected_pane_index = 0
    assert not app.itable[4].will_import

#---
def app_import_checkbook_qif_with_existing_txns():
    # The end result of this setup is that only the 2nd existing entry end up in the table 
    # (the first is reconciled)
    app = TestApp()
    app.add_account('foo')
    app.mw.show_account()
    app.add_entry(date='01/01/2007', description='first entry', increase='1')
    app.aview.toggle_reconciliation_mode()
    app.etable.toggle_reconciled()
    app.aview.toggle_reconciliation_mode() # commit
    app.add_entry(date='02/01/2007', description='second entry', increase='2')
    app.doc.date_range = YearRange(date(2007, 1, 1))
    app.doc.parse_file_for_import(TestData.filepath('qif', 'checkbook.qif'))
    app.clear_gui_calls()
    app.iwin.selected_target_account_index = 1 # foo
    app.check_gui_calls(app.itable_gui, ['refresh'])
    return app

@with_app(app_import_checkbook_qif_with_existing_txns)
def test_bind(app):
    # Binding 2 entries removes the imported entry and places it at the existing's row.
    app.itable.bind(2, 4) # now, we shouldn't put the 3rd entry after the 5th in the sort order
    eq_(len(app.itable), 5)
    eq_(app.itable[2].date, '02/01/2007')
    eq_(app.itable[2].description, 'second entry')
    eq_(app.itable[2].amount, '2.00')
    eq_(app.itable[2].date_import, '02/01/2007')
    eq_(app.itable[2].description_import, 'Power Bill')
    eq_(app.itable[2].amount_import, '-57.12')
    app.check_gui_calls(app.itable_gui, ['refresh'])

@with_app(app_import_checkbook_qif_with_existing_txns)
def test_can_bind(app):
    # can_bind() returns True only when trying to bind 2 rows with opposite missing elements.
    assert app.itable.can_bind(2, 3) # existing --> import
    assert app.itable.can_bind(3, 2) # import --> existing
    assert not app.itable.can_bind(1, 3) # import --> import

@with_app(app_import_checkbook_qif_with_existing_txns)
def test_is_two_sided_with_target_account(app):
    # We have a target account, and some transactions can be bound in it. The table is 
    # two-sided.
    assert app.itable.is_two_sided

@with_app(app_import_checkbook_qif_with_existing_txns)
def test_rows_mixed_with_existing_rows(app):
    # Imported rows are mixed with existing rows.
    eq_(len(app.itable), 6) # only unreconciled entries
    # The 1st and 2nd imported entries are on 01/01 and the 3rd is on 02/01. Existing entries
    # come before in the sort order, so the existing entry is placed 3rd.
    eq_(app.itable[2].date, '02/01/2007')
    eq_(app.itable[2].description, 'second entry')
    eq_(app.itable[2].amount, '2.00')
    eq_(app.itable[2].date_import, '')
    eq_(app.itable[2].description_import, '')
    eq_(app.itable[2].amount_import, '')
    # will_import is False and can't be set
    assert not app.itable[2].can_edit_will_import
    assert not app.itable[2].will_import
    app.itable[2].will_import = True
    assert not app.itable[2].will_import

#---
def app_import_with_empty_target_account():
    app = TestApp()
    app.add_account('foo')
    app.doc.parse_file_for_import(TestData.filepath('qif', 'checkbook.qif'))
    app.iwin.selected_target_account_index = 1 # foo
    return app

@with_app(app_import_with_empty_target_account)
def test_is_two_sided_with_empty_target_account(app):
    # We have a target account, but no bindable txns to show. The table is one-sided.
    assert not app.itable.is_two_sided

#---
def app_load_then_import_with_references():
    # with_reference1 and 2 have references that overlap. This is supposed to cause matching in the
    # import dialog.
    app = TestApp()
    app.doc.load_from_xml(TestData.filepath('moneyguru', 'with_references1.moneyguru'))
    app.doc.date_range = YearRange(date(2008, 1, 1))
    app.doc.parse_file_for_import(TestData.filepath('moneyguru', 'with_references2.moneyguru'))
    app.clear_gui_calls()
    return app

@with_app(app_load_then_import_with_references)
def test_can_bind_when_already_bound(app):
    # can_bind() returns False when a bound entry is involved.
    assert not app.itable.can_bind(0, 1) # existing --> bound
    assert not app.itable.can_bind(1, 0) # bound --> existing
    assert not app.itable.can_bind(1, 2) # bound --> imported
    assert not app.itable.can_bind(2, 1) # imported --> bound

@with_app(app_load_then_import_with_references)
def test_reconciled_entry_match(app):
    # When an entry with reference is reconciled, the match is added, but will_import defaults
    # to False
    assert not app.itable[1].will_import

@with_app(app_load_then_import_with_references)
def test_rows_with_references_matching(app):
    # There are 4 txns in both of the files. However, 2 of them have the same reference, so
    # we end up with 3 entries.
    eq_(len(app.itable), 3)
    eq_(app.itable[0].date, '15/02/2008')
    eq_(app.itable[0].description, 'txn1')
    eq_(app.itable[0].amount, 'CAD 42.00')
    eq_(app.itable[0].date_import, '')
    eq_(app.itable[0].description_import, '')
    eq_(app.itable[0].amount_import, '')
    assert not app.itable[0].bound
    eq_(app.itable[1].date, '16/02/2008')
    eq_(app.itable[1].description, 'txn2')
    eq_(app.itable[1].amount, 'CAD -14.00')
    eq_(app.itable[1].date_import, '16/02/2008')
    eq_(app.itable[1].description_import, 'txn2')
    eq_(app.itable[1].amount_import, 'CAD -14.00')
    assert app.itable[1].bound
    eq_(app.itable[2].date, '')
    eq_(app.itable[2].description, '')
    eq_(app.itable[2].amount, '')
    eq_(app.itable[2].date_import, '20/02/2008')
    eq_(app.itable[2].description_import, 'txn5')
    eq_(app.itable[2].amount_import, 'CAD 50.00')
    assert not app.itable[2].bound

@with_app(app_load_then_import_with_references)
def test_unbind(app):
    # unbind_selected() unbinds the selected match.
    app.itable.unbind(1)
    eq_(len(app.itable), 4)
    eq_(app.itable[1].date, '16/02/2008')
    eq_(app.itable[1].description, 'txn2')
    eq_(app.itable[1].amount, 'CAD -14.00')
    eq_(app.itable[1].date_import, '')
    eq_(app.itable[1].description_import, '')
    eq_(app.itable[1].amount_import, '')
    eq_(app.itable[2].date, '')
    eq_(app.itable[2].description, '')
    eq_(app.itable[2].amount, '')
    eq_(app.itable[2].date_import, '16/02/2008')
    eq_(app.itable[2].description_import, 'txn2')
    eq_(app.itable[2].amount_import, 'CAD -14.00')
    app.check_gui_calls(app.itable_gui, ['refresh'])

@with_app(app_load_then_import_with_references)
def test_unbind_unbound(app):
    # Trying to unbind an unbound match has no effect.
    app.itable.unbind(0)
    eq_(len(app.itable), 3)
    app.itable.unbind(2)
    eq_(len(app.itable), 3)
