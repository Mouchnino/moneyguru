# Created By: Virgil Dupras
# Created On: 2008-07-05
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_
from hscommon.currency import CAD, EUR

from ..base import TestApp, with_app

#--- One entry
def app_one_entry():
    app = TestApp()
    app.add_account('first', currency=CAD)
    app.mainwindow.show_account()
    app.add_entry(transfer='second', increase='42')
    return app

def test_add_gui_calls():
    # refresh() and start_editing() are called after a add()
    app = app_one_entry()
    app.tpanel.load()
    app.clear_gui_calls()
    app.stable.add()
    app.stable.view.check_gui_calls(['refresh', 'start_editing', 'stop_editing'])

def test_cancel_edits():
    # cancel_edits() sets edited to None and makes the right gui calls
    app = app_one_entry()
    app.tpanel.load()
    app.stable[0].account = 'foo'
    app.clear_gui_calls()
    app.stable.cancel_edits()
    assert app.stable.edited is None
    app.stable.view.check_gui_calls(['refresh', 'stop_editing'])

@with_app(app_one_entry)
def test_cancel_edits_while_adding(app):
    # cancel_edits() removes edited row if it was being added
    app.tpanel.load()
    app.stable.add()
    app.stable[2].account = 'foo'
    app.stable.cancel_edits()
    eq_(len(app.stable), 2)

def test_changes_split_buffer_only():
    # Changes made to the split table don't directly get to the model until tpanel.save().
    app = app_one_entry()
    app.tpanel.load()
    row = app.stable.selected_row
    row.debit = '40'
    app.stable.save_edits()
    # Now, let's force a refresh of etable
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    eq_(app.etable[0].increase, 'CAD 42.00')

def test_completion():
    # Just make sure it works. That is enough to know SplitTable is of the right subclass.
    app = app_one_entry()
    ce = app.completable_edit('account')
    ce.text = 's'
    eq_(ce.completion, 'econd')

def test_completion_new_txn():
    # When completing an account from a new txn, the completion wouldn't work at all
    app = app_one_entry()
    app.show_tview()
    app.ttable.add()
    app.tpanel.load()
    ce = app.completable_edit('account')
    ce.text = 'f'
    eq_(ce.completion, 'irst')

def test_load_tpanel_from_ttable():
    # When the tpanel is loaded form the ttable, the system currency is used.
    app = app_one_entry()
    app.show_tview()
    app.tpanel.load() # no crash
    eq_(app.stable[0].debit, 'CAD 42.00')

def test_memo():
    # It's possible to set a different memo for each split.
    app = app_one_entry()
    app.tpanel.load()
    row = app.stable.selected_row
    row.memo = 'memo1'
    app.stable.save_edits()
    app.stable.select([1])
    row = app.stable.selected_row
    row.memo = 'memo2'
    app.stable.save_edits()
    app.tpanel.save()
    app.tpanel.load()
    eq_(app.stable[0].memo, 'memo1')
    eq_(app.stable[1].memo, 'memo2')

def test_set_wrong_values_for_attributes():
    # set_attribute_value catches ValueError.
    app = app_one_entry()
    app.tpanel.load()
    row = app.stable.selected_row
    app.debit = 'invalid'
    app.credit = 'invalid'
    # no crash occured

#--- Transaction being added
def app_transaction_being_added():
    app = TestApp()
    app.show_tview()
    app.ttable.add()
    return app

@with_app(app_transaction_being_added)
def test_change_splits(app):
    # It's possible to change the splits of a newly created transaction.
    # Previously, it would crash because of the 0 amounts.
    # At this moment, we have a transaction with 2 empty splits
    app.tpanel.load()
    app.stable[0].account = 'first'
    app.stable[0].credit = '42'
    app.stable.save_edits()
    app.stable.select([1])
    app.stable[1].account = 'second'
    app.stable.save_edits()
    app.tpanel.save()
    row = app.ttable[0]
    eq_(row.from_, 'first')
    eq_(row.to, 'second')
    eq_(row.amount, '42.00')

@with_app(app_transaction_being_added)
def test_delete_split_with_none_selected(app):
    # don't crash when stable.delete() is called enough times to leave the table empty
    app.tpanel.load()
    app.stable.delete() # Unassigned 1
    app.stable.delete() # Unassigned 2
    try:
        app.stable.delete()
    except AttributeError:
        raise AssertionError("When the table is empty, don't try to delete")

#--- Transaction with splits
def app_transaction_with_splits():
    app = TestApp()
    app.add_txn(from_='foo', to='bar', amount='42')
    app.mainwindow.edit_item()
    app.stable.add()
    app.stable[2].account = 'baz'
    app.stable[2].credit = '3'
    app.stable.save_edits()
    return app

def test_auto_decimal_place():
    # the auto decimal place options affects the split table.
    app = app_transaction_with_splits()
    app.app.auto_decimal_place = True
    app.stable[0].debit = '1234'
    eq_(app.stable[0].debit, '12.34')

def test_move_split():
    # It's possible to move splits around
    app = app_transaction_with_splits()
    # order of first 2 splits is not defined
    first_account = app.stable[0].account
    second_account = app.stable[1].account
    app.stable.move_split(1, 0)
    eq_(app.stable[0].account, second_account)
    eq_(app.stable.selected_indexes, [0])
    app.stable.move_split(1, 2)
    eq_(app.stable[2].account, first_account)
    eq_(app.stable.selected_indexes, [2])

#--- EUR account and EUR transfer
def app_eur_account_and_eur_transfer():
    app = TestApp()
    app.add_account('first', EUR)
    app.add_account('second', EUR)
    app.mw.show_account()
    app.add_entry(transfer='first', increase='42') # EUR
    app.tpanel.load()
    return app

def test_amounts_display():
    # The amounts' currency are explicitly displayed.
    app = app_eur_account_and_eur_transfer()
    eq_(app.stable[0].debit, 'EUR 42.00')
    eq_(app.stable[1].credit, 'EUR 42.00')

def test_change_amount_implicit_currency():
    # When typing a currency-less amount, the transaction amount's currency is used.
    app = app_eur_account_and_eur_transfer()
    app.stable[0].debit = '64'
    eq_(app.stable[0].debit, 'EUR 64.00')
