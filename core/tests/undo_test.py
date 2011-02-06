# Created By: Virgil Dupras
# Created On: 2008-06-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import copy
import time
from datetime import date

from hscommon.testutil import eq_, patch_today
from hscommon.currency import EUR

from ..const import PaneType
from ..document import ScheduleScope
from ..model.date import MonthRange
from ..model.account import AccountType
from .base import compare_apps, testdata, TestApp, with_app

def copydoc(doc):
    # doing a deepcopy on the document itself makes a deepcopy of *all* guis because they're
    # listeners. What we do is a shallow copy of it, *then* a deepcopy of stuff we compare
    # afterwards.
    newdoc = copy.copy(doc)
    newdoc.accounts = copy.deepcopy(newdoc.accounts)
    newdoc.groups = copy.deepcopy(newdoc.groups)
    newdoc.transactions = copy.deepcopy(newdoc.transactions)
    newdoc.schedules = copy.deepcopy(newdoc.schedules)
    newdoc.budgets = copy.deepcopy(newdoc.budgets)
    return newdoc

def pytest_funcarg__checkstate(request):
    app = request.getfuncargvalue('app')
    previous_state = copydoc(app.doc)
    def docheck():
        before_undo = copydoc(app.doc)
        app.doc.undo()
        compare_apps(previous_state, app.doc)
        app.doc.redo()
        compare_apps(before_undo, app.doc)
    return docheck

#---
@with_app(TestApp)
def test_can_redo_initially(app):
    # can_redo is initially false.
    assert not app.doc.can_redo()

@with_app(TestApp)
def test_can_undo_initially(app):
    # can_undo is initially false.
    assert not app.doc.can_undo()

@with_app(TestApp)
def test_descriptions_initially(app):
    # undo/redo descriptions are None.
    assert app.doc.undo_description() is None
    assert app.doc.redo_description() is None

@with_app(TestApp)
def test_undo_add_account(app, checkstate):
    # Undo after an add_account() removes that account.
    app.bsheet.add_account()
    checkstate()

@with_app(TestApp)
def test_undo_add_group(app, checkstate):
    # It's possible to undo the addition of an account group.
    app.bsheet.add_account_group()
    checkstate()

@with_app(TestApp)
def test_add_schedule(app, checkstate):
    # schedule addition are undoable
    app.mw.select_schedule_table()
    app.scpanel.new()
    app.scpanel.save()    
    checkstate()

@with_app(TestApp)
def test_add_transaction(app, checkstate):
    # It's possible to undo a transaction addition (from the ttable).
    app.ttable.add()
    row = app.ttable.edited
    # make sure that aut-created accounts go away as well.
    row.from_ = 'foo'
    row.to = 'bar'
    app.ttable.save_edits()
    checkstate()

@with_app(TestApp)
def test_import(app, checkstate):
    # When undoing an import that creates income/expense accounts, don't crash on auto account
    # removal
    app.doc.parse_file_for_import(testdata.filepath('qif', 'checkbook.qif'))
    app.iwin.import_selected_pane()
    checkstate()

@with_app(TestApp)
def test_undo_shown_account(app):
    # Undoing the creation of a new account when shown sets makes the main window go back to
    # the net worth sheet *before* triggering a refresh (otherwise, we crash).
    app.mw.select_income_statement()
    app.mw.new_item()
    app.mw.show_account()
    app.doc.undo() # no crash

#---
def app_one_nameless_account():
    app = TestApp()
    app.add_account()
    return app
    
@with_app(app_one_nameless_account)
def test_undo_apanel_attrs(app, checkstate):
    # Undoing a changes made from apanel work
    app.mw.edit_item()
    app.apanel.currency = EUR
    app.apanel.account_number = '1234'
    app.apanel.notes = 'some notes'
    app.apanel.save()
    checkstate()

#---
def app_one_named_account():
    app = TestApp()
    app.add_account('foobar')
    app.mw.show_account()
    return app

@with_app(app_one_named_account)
def test_action_after_undo(app):
    # When doing an action after an undo, the whole undo chain is broken at the current index.
    app.doc.undo() # undo set name
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.selected.name = 'foobaz'
    app.bsheet.save_edits()
    app.doc.undo() # undo set name
    app.doc.redo()
    eq_(app.bsheet.assets[0].name, 'foobaz')
    assert not app.doc.can_redo()
    app.doc.undo()
    app.doc.undo() # undo add account
    eq_(app.bsheet.assets.children_count, 2)

@with_app(app_one_named_account)
def test_can_redo_after_action(app):
    # can_redo is false as long as an undo hasn't been performed.
    assert not app.doc.can_redo()
    app.doc.undo()
    assert app.doc.can_redo() # now we can redo()

@with_app(app_one_named_account)
def test_can_undo_after_action(app):
    # Now that an account has been added, can_undo() is True.
    assert app.doc.can_undo()
    app.doc.undo()
    app.doc.undo()
    assert not app.doc.can_undo()

@with_app(app_one_named_account)
def test_change_account_on_duplicate_account_name_doesnt_record_action(app):
    # Renaming an account and causing a duplicate account name error doesn't cause an action to
    # be recorded
    app.mainwindow.select_balance_sheet()
    app.bsheet.add_account()
    app.bsheet.selected.name = 'foobar'
    app.bsheet.save_edits()
    eq_(app.doc.undo_description(), 'Add account') # We're still at undoing the add

@with_app(app_one_named_account)
def test_descriptions_after_action(app):
    # The undo/redo description system works properly.
    eq_(app.doc.undo_description(), 'Change account')
    assert app.doc.redo_description() is None
    app.doc.undo()
    eq_(app.doc.undo_description(), 'Add account')
    eq_(app.doc.redo_description(), 'Change account')
    app.doc.undo()
    assert app.doc.undo_description() is None
    eq_(app.doc.redo_description(), 'Add account')
    app.doc.redo()
    eq_(app.doc.undo_description(), 'Add account')
    eq_(app.doc.redo_description(), 'Change account')
    app.doc.redo()
    eq_(app.doc.undo_description(), 'Change account')
    assert app.doc.redo_description() is None

@with_app(app_one_named_account)
def test_description_after_delete(app):
    # the undo description is 'Remove account' after deleting an account.
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    eq_(app.doc.undo_description(), 'Remove account')

@with_app(app_one_named_account)
def test_gui_calls(app):
    # the correct gui calls are made when undoing/redoing (in particular: stop_editing)
    app.mainwindow.select_balance_sheet()
    app.clear_gui_calls()
    app.doc.undo()
    app.check_gui_calls(app.bsheet_gui, ['refresh', 'stop_editing'])
    app.doc.redo()
    app.check_gui_calls(app.bsheet_gui, ['refresh', 'stop_editing'])

@with_app(app_one_named_account)
def test_modified_status(app, tmpdir):
    filepath = str(tmpdir.join('foo.moneyguru'))
    app.doc.save_to_xml(filepath)
    assert not app.doc.is_dirty()
    app.add_entry()
    assert app.doc.is_dirty()
    app.doc.undo()
    assert not app.doc.is_dirty()
    app.doc.redo()
    assert app.doc.is_dirty()
    app.doc.undo()
    assert not app.doc.is_dirty()
    app.doc.undo()
    assert app.doc.is_dirty()
    app.doc.redo()
    assert not app.doc.is_dirty()
    app.doc.undo()
    app.doc.undo()
    assert app.doc.is_dirty()

@with_app(app_one_named_account)
def test_redo_delete_while_in_etable(app):
    # If we're in etable and perform a redo that removes the account we're in, go back to the bsheet
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    app.doc.undo()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    app.clear_gui_calls()
    app.doc.redo()
    app.check_current_pane(PaneType.NetWorth)
    expected = ['view_closed', 'change_current_pane', 'refresh_undo_actions', 'refresh_status_line']
    app.check_gui_calls(app.mainwindow_gui, expected)

@with_app(app_one_named_account)
def test_undo_add_entry(app, checkstate):
    # Undoing an entry addition works in one shot (not one shot to blank the fields then one 
    # other shot to remove the transaction.
    app.add_entry(description='foobar')
    checkstate()

@with_app(app_one_named_account)
def test_undo_delete_account(app, checkstate):
    # Undo after having removed an account puts it back in.
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    checkstate()

@with_app(app_one_named_account)
def test_undo_move_account(app, checkstate):
    # Moving an account from one section to another can be undone
    app.mainwindow.select_balance_sheet()
    app.bsheet.move([0, 0], [1])
    checkstate()

@with_app(app_one_named_account)
def test_undo_set_account_name(app, checkstate):
    # Undo after a name change puts back the old name.
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.selected.name = 'foobaz'
    app.bsheet.save_edits()
    checkstate()

@with_app(app_one_named_account)
def test_undo_add_while_in_etable(app):
    # If we're in etable and perform an undo that removes the account we're in, go back to the bsheet
    app.mainwindow.select_entry_table()
    app.doc.undo()
    app.clear_gui_calls()
    app.doc.undo()
    app.check_current_pane(PaneType.NetWorth)
    expected = ['view_closed', 'change_current_pane', 'refresh_undo_actions', 'refresh_status_line']
    app.check_gui_calls(app.mainwindow_gui, expected)

@with_app(app_one_named_account)
def test_undo_twice(app):
    # Undoing a new_account() just after having undone a change_account works.
    # Previously, a copy of the changed account would be inserted, making it impossible for
    # undo to find the account to be removed.
    app.mainwindow.select_balance_sheet()
    app.doc.undo()
    app.doc.undo()
    eq_(app.bsheet.assets.children_count, 2)

#---
def app_account_group():
    app = TestApp()
    app.add_group()
    return app

@with_app(app_account_group)
def test_descriptions_after_group(app):
    # All group descriptions are there.
    eq_(app.doc.undo_description(), 'Add group')
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.selected.name = 'foobar'
    app.bsheet.save_edits()
    eq_(app.doc.undo_description(), 'Change group')
    app.bsheet.delete()
    eq_(app.doc.undo_description(), 'Remove group')

@with_app(app_account_group)
def test_undo_delete_group(app, checkstate):
    # It's possible to undo group deletion.
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    checkstate()

@with_app(app_account_group)
def test_undo_rename_group(app, checkstate):
    # It's possible to undo a group rename.
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.selected.name = 'foobar'
    app.bsheet.save_edits()
    checkstate()

#---
def app_account_in_group():
    app = TestApp()
    app.add_group('group')
    app.add_account(group_name='group')
    app.mainwindow.show_account()
    return app

@with_app(app_account_in_group)
def test_change_group_on_duplicate_account_name_doesnt_record_action(app):
    # Renaming a group and causing a duplicate account name error doesn't cause an action to
    # be recorded
    app.mainwindow.select_balance_sheet()
    app.bsheet.add_account_group()
    app.bsheet.selected.name = 'group'
    app.bsheet.save_edits()
    eq_(app.doc.undo_description(), 'Add group') # We're still at undoing the add

@with_app(app_account_in_group)
def test_undo_delete_group_with_account(app, checkstate):
    # When undoing a group deletion, the accounts that were in it are back in.
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    checkstate()

@with_app(app_account_in_group)
def test_undo_move_account_out_of_group(app, checkstate):
    # Undoing a move_account for an account that was in a group puts it back in that group.
    app.mainwindow.select_balance_sheet()
    app.bsheet.move([0, 0, 0], [1])
    checkstate()

#---
def app_load_file():
    # Loads 'simple.moneyguru', a file with 2 accounts and 2 entries in each. Select the first entry.
    app = TestApp()
    app.doc.date_range = MonthRange(date(2008, 2, 1))
    # This is to set the modified flag to true so we can make sure it has been put back to false
    app.add_account()
    app.doc.load_from_xml(testdata.filepath('moneyguru', 'simple.moneyguru'))
    # we have to cheat here because the first save state is articifially
    # different than the second save state because the second state has
    # the currency rates fetched. So what we do here is wait a little bit
    # and recook.
    time.sleep(0.05)
    app.doc._cook()
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    return app

@with_app(app_load_file)
def test_can_undo(app):
    # can_undo becomes false after a load.
    assert not app.doc.can_undo()

@with_app(app_load_file)
def test_undo_add_account_in_group(app, checkstate):
    # The undoer keeps its account list up-to-date after a load.
    # Previously, the Undoer would hold an old instance of AccountList
    app.bsheet.add_account()
    checkstate()

@with_app(app_load_file)
def test_undo_add_entry_in_grouped_account(app, checkstate):
    # The undoer keeps its transaction list up-to-date after a load.
    # Previously, the Undoer would hold an old instance of TransactionList
    app.add_entry(description='foobar', transfer='some_account', increase='42')
    checkstate()

@with_app(app_load_file)
def test_undo_add_group_besides_account_in_group(app, checkstate):
    # The undoer keeps its group list up-to-date after a load.
    # Previously, the Undoer would hold an old instance of GroupList
    app.mainwindow.select_balance_sheet()
    app.bsheet.add_account_group()
    checkstate()

#---
def app_two_txns_in_two_accounts():
    # 2 accounts, 1 transaction that is a transfer between the 2 accounts, and 1 transaction that
    # is imbalanced.
    app = TestApp()
    app.add_account('first')
    app.add_account('second')
    app.show_account('first')
    app.add_entry('19/6/2008', transfer='second')
    app.add_entry('20/6/2008', description='description', payee='payee', increase='42', checkno='12')
    return app

@with_app(app_two_txns_in_two_accounts)
def test_descriptions_after_add_txn(app):
    # All transaction descriptions are there.
    eq_(app.doc.undo_description(), 'Add transaction')
    row = app.etable.selected_row
    row.description = 'foobar'
    app.etable.save_edits()
    eq_(app.doc.undo_description(), 'Change transaction')
    app.etable.delete()
    eq_(app.doc.undo_description(), 'Remove transaction')

@with_app(app_two_txns_in_two_accounts)
def test_etable_refreshes(app):
    app.clear_gui_calls()
    app.doc.undo()
    eq_(app.etable_count(), 1)
    app.check_gui_calls(app.etable_gui, ['refresh', 'stop_editing'])

@with_app(app_two_txns_in_two_accounts)
def test_ttable_refreshes(app):
    app.mainwindow.select_transaction_table()
    app.clear_gui_calls()
    app.doc.undo()
    eq_(app.ttable.row_count, 1)
    app.check_gui_calls(app.ttable_gui, ['refresh', 'stop_editing'])

@with_app(app_two_txns_in_two_accounts)
def test_undo_change_transaction_from_etable(app, checkstate):
    # It's possible to undo a transaction change.
    row = app.etable.selected_row
    row.date = '21/6/2008'
    row.description = 'foo'
    row.payee = 'baz'
    row.transfer = 'third'
    row.decrease = '34'
    row.checkno = '15'
    app.etable.save_edits()
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_change_transaction_from_ttable(app, checkstate):
    # It's possible to undo a transaction change.
    app.mainwindow.select_transaction_table()
    row = app.ttable[1]
    row.date = '21/6/2008'
    row.description = 'foo'
    row.payee = 'baz'
    row.from_ = 'third'
    row.to = 'fourth'
    row.amount = '34'
    row.checkno = '15'
    app.ttable.save_edits()
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_delete_entry(app, checkstate):
    # It's possible to undo a transaction deletion.
    app.etable.select([0, 1])
    app.etable.delete()
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_delete_transaction(app, checkstate):
    # It's possible to undo a transaction deletion.
    app.mainwindow.select_transaction_table()
    app.ttable.select([0, 1])
    app.ttable.delete()
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_delete_account_with_txn(app, checkstate):
    # When 'first' is deleted, one transaction is simply unbound, and the other is deleted. we 
    # must undo all that
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    app.arpanel.save() # continue deletion
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_duplicate_transaction(app, checkstate):
    app.mainwindow.select_transaction_table()
    app.ttable.select([0, 1])
    app.ttable.duplicate_selected()
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_mass_edition(app, checkstate):
    # Mass edition can be undone.
    app.etable.select([0, 1])
    app.mepanel.load()
    app.mepanel.description_enabled = True
    app.mepanel.description = 'foobar'
    app.mepanel.save()
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_schedule(app, checkstate):
    app.tpanel.load()
    app.tpanel.repeat_index = 1 # daily
    app.tpanel.save()
    checkstate()

@with_app(app_two_txns_in_two_accounts)
def test_undo_schedule_entry_transfer(app):
    # After undoing a scheduling, the entry has the wrong transfer
    app.etable.select([0])
    app.tpanel.load()
    app.tpanel.repeat_index = 1 # daily
    app.tpanel.save()
    app.doc.undo()
    eq_(app.etable[0].transfer, 'second')

#---
def app_two_txns_same_date():
    app = TestApp()
    app.add_account()
    app.mainwindow.show_account()
    app.add_entry('19/6/2008', description='first')
    app.add_entry('19/6/2008', description='second')
    return app

@with_app(app_two_txns_same_date)
def test_undo_delete_first_transaction(app, checkstate):
    # When undoing a deletion, the entry comes back at the same position.
    app.etable.select([0])
    app.etable.delete()
    checkstate()

@with_app(app_two_txns_same_date)
def test_undo_reorder_entry(app, checkstate):
    # Reordering can be undone.
    app.etable.move([1], 0)
    checkstate()

#---
def app_three_txns_reconciled():
    app = TestApp()
    app.add_account()
    app.mainwindow.show_account()
    app.add_entry('19/6/2008', description='first')
    app.add_entry('19/6/2008', description='second')
    app.add_entry('20/6/2008', description='third')
    app.aview.toggle_reconciliation_mode()
    app.etable[0].toggle_reconciled()
    app.etable[1].toggle_reconciled()
    app.etable[2].toggle_reconciled()
    app.aview.toggle_reconciliation_mode() # commit
    return app

@with_app(app_three_txns_reconciled)
def test_change_entry(app, checkstate):
    # Performing a txn change that results in unreconciliation can be completely undone
    # (including the unreconciliation).
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    app.etable[0].date = '18/6/2008'
    app.etable.save_edits()
    checkstate()

@with_app(app_three_txns_reconciled)
def test_change_transaction(app, checkstate):
    # Performing a txn change that results in unreconciliation can be completely undone
    # (including the unreconciliation).
    app.mainwindow.select_transaction_table()
    app.ttable[0].date = '18/6/2008'
    app.ttable.save_edits()
    checkstate()

@with_app(app_three_txns_reconciled)
def test_delete_transaction(app, checkstate):
    # Deleting txn change that results in unreconciliation can be completely undone
    # (including the unreconciliation).
    app.mainwindow.select_transaction_table()
    app.ttable.delete()
    checkstate()

@with_app(app_three_txns_reconciled)
def test_move_transaction(app, checkstate):
    # Moving txn change that results in unreconciliation can be completely undone
    # (including the unreconciliation).
    app.mainwindow.select_transaction_table()
    app.ttable.move([0], 2)
    checkstate()

@with_app(app_three_txns_reconciled)
def test_toggle_reconciled(app, checkstate):
    # reconciliation toggling is undoable
    app.aview.toggle_reconciliation_mode()
    app.etable[1].toggle_reconciled()
    checkstate()

#---
def app_import_ofx():
    app = TestApp()
    app.doc.date_range = MonthRange(date(2008, 2, 1))
    app.doc.parse_file_for_import(testdata.filepath('ofx', 'desjardins.ofx'))
    app.iwin.import_selected_pane()
    # same cheat as in LoadFile
    time.sleep(0.05)
    app.doc._cook()
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    return app

@with_app(app_import_ofx)
def test_description_after_import(app):
    # The undo description is 'Import'.
    eq_(app.doc.undo_description(), 'Import')

@with_app(app_import_ofx)
def test_undo_delete_transaction_with_import_ref(app, checkstate):
    # When undoing a transaction's deletion which had a reference, actually put it back in.
    # Previously, the reference stayed in the dictionary, making it as if
    # the transaction was still there
    app.etable.delete()
    checkstate()

@with_app(app_import_ofx)
def test_undo_import(app, checkstate):
    # Undoing an import removes all accounts and transactions added by  that import. It also
    # undo changes that have been made.
    app.doc.parse_file_for_import(testdata.filepath('ofx', 'desjardins2.ofx'))
    # this is the pane that has stuff in it
    app.iwin.selected_target_account_index = 1
    app.iwin.import_selected_pane()
    checkstate()

#---
def app_with_autocreated_transfer():
    app = TestApp()
    app.add_account()
    app.mainwindow.show_account()
    app.add_entry('19/6/2008', transfer='auto')
    return app

@with_app(app_with_autocreated_transfer)
def test_undo_delete_transaction_brings_back_auto_created_account(app, checkstate):
    # When undoing the deletion of a transaction that results in the removal of an
    # income/expense account, bring that account back.
    app.etable.delete()
    checkstate()

#---
def app_scheduled_txn():
    app = TestApp()
    app.add_account('account')
    app.add_schedule(description='foobar', account='account')
    app.mainwindow.select_schedule_table()
    app.sctable.select([0])
    return app

@with_app(app_scheduled_txn)
def test_change_schedule(app, checkstate):
    app.scpanel.load()
    app.scpanel.description = 'changed'
    app.scpanel.repeat_every = 12
    app.scpanel.save()
    checkstate()

@with_app(app_scheduled_txn)
def test_change_spawn_globally(app):
    # Changing a spawn globally then undoing correcty updates the spawns. Old values would
    # previously linger around even though the schedule had been un-changed.
    app.mainwindow.select_transaction_table()
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.select([0])
    app.ttable[0].description = 'changed'
    app.ttable.save_edits()
    app.doc.undo()
    eq_(app.ttable[1].description, 'foobar')

@with_app(app_scheduled_txn)
def test_delete_account(app, checkstate):
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    app.arpanel.save()
    checkstate()

@with_app(app_scheduled_txn)
def test_delete_schedule(app, checkstate):
    app.sctable.delete()
    checkstate()

@with_app(app_scheduled_txn)
def test_delete_spawn_undo_then_delete_again(app):
    # There was a bug where a spawn deletion being undone would result in an undeletable spawn
    # being put back into the ttable.
    app.mainwindow.select_transaction_table()
    app.ttable.select([0])
    app.ttable.delete()
    app.doc.undo()
    # we don't care about the exact len, we just care that it decreases by 1
    len_before = app.ttable.row_count
    app.ttable.select([0])
    app.ttable.delete()
    eq_(app.ttable.row_count, len_before-1)

@with_app(app_scheduled_txn)
def test_reconcile_spawn_by_changing_recdate(app, checkstate):
    # Undoing a spawn reconciliation correctly removes the materialized txn.
    app.show_account('account')
    app.etable[0].reconciliation_date = app.etable[0].date
    app.etable.save_edits()
    checkstate()

@with_app(app_scheduled_txn)
def test_reconcile_spawn_by_toggling(app, checkstate):
    # Undoing a spawn reconciliation correctly removes the materialized txn.
    app.show_account('account')
    app.aview.toggle_reconciliation_mode()
    app.etable[0].toggle_reconciled()
    checkstate()

#---
def app_with_budget(monkeypatch):
    app = TestApp()
    patch_today(monkeypatch, 2008, 1, 27)
    app.drsel.select_today_date_range()
    app.add_account('Some Expense', account_type=AccountType.Expense)
    app.add_budget('Some Expense', None, '100')
    app.mainwindow.select_budget_table()
    app.btable.select([0])
    return app

@with_app(app_with_budget)
def test_change_budget(app, checkstate):
    app.bpanel.load()
    app.bpanel.repeat_every = 12
    app.bpanel.save()
    checkstate()

@with_app(app_with_budget)
def test_delete_account_with_budget(app, checkstate):
    app.mainwindow.select_income_statement()
    app.istatement.selected = app.istatement.expenses[0]
    app.istatement.delete()
    app.arpanel.save()
    checkstate()

@with_app(app_with_budget)
def test_delete_budget(app, checkstate):
    app.btable.delete()
    checkstate()
