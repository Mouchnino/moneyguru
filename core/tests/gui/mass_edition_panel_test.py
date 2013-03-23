# Created By: Virgil Dupras
# Created On: 2008-07-25
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from pytest import raises
from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...exception import OperationAborted

#--- Pristine
@with_app(TestApp)
def test_can_load_when_empty(app):
    # When there's no selection, loading the panel raises OperationAborted
    with raises(OperationAborted):
        app.mepanel.load()

#--- Two Transactions
def app_two_transactions():
    app = TestApp()
    app.show_tview()
    app.ttable.add()
    app.ttable.save_edits()
    app.ttable.add()
    app.ttable.save_edits()
    return app

@with_app(app_two_transactions)
def test_can_load_when_one_txn_selected(app):
    # When there is only one txn selected, loading the panel raises OperationAborted
    with raises(OperationAborted):
        app.mepanel.load()

@with_app(app_two_transactions)
def test_can_load_after_selection(app):
    # When there is more than one txn selected, load() can be called
    # This test has a collateral, which is to make sure that mepanel doesn't have a problem
    # loading txns with splits with None accounts.
    app.ttable.select([0, 1])
    app.mepanel.load() # No OperationAborted

@with_app(app_two_transactions)
def test_save_out_of_range_currency_index(app):
    # When the currency index is out of range, don't crash.
    # (On OS X, when typing a currency that doesn't exist in the box, the index ends up being an
    # out of range one)
    app.mw.edit_item()
    app.mepanel.currency_list.select(999999)
    app.mepanel.save() # no crash

@with_app(app_two_transactions)
def test_saving_nothing_does_nothing(app):
    # Don't initiate a transaction change if nothing is changed in the panel.
    app.save_file()
    app.mw.edit_item()
    app.mepanel.save()
    assert not app.doc.is_dirty()

#--- Two transactions different values
def app_two_transactions_different_value():
    app = TestApp()
    app.add_account('from1')
    app.show_account()
    app.add_entry(date='06/07/2008', description='description1', payee='payee1', checkno='42', transfer='to1', decrease='42')
    app.add_account('from2')
    app.show_account()
    app.add_entry(date='07/07/2008', description='description2', payee='payee2', checkno='43', transfer='to2', decrease='43')
    app.show_tview()
    app.ttable.select([0, 1])
    app.mepanel.load()
    return app

def test_attributes(monkeypatch):
    # All fields are disabled and empty.
    monkeypatch.patch_today(2010, 2, 20)
    app = app_two_transactions_different_value()
    assert app.mepanel.can_change_accounts
    assert app.mepanel.can_change_amount
    assert not app.mepanel.date_enabled
    assert not app.mepanel.description_enabled
    assert not app.mepanel.payee_enabled
    assert not app.mepanel.checkno_enabled
    assert not app.mepanel.from_enabled
    assert not app.mepanel.to_enabled
    assert not app.mepanel.amount_enabled
    eq_(app.mepanel.date_field.text, '20/02/2010')
    eq_(app.mepanel.description_field.text, '')
    eq_(app.mepanel.payee_field.text, '')
    eq_(app.mepanel.checkno_field.text, '')
    eq_(app.mepanel.from_field.text, '')
    eq_(app.mepanel.to_field.text, '')
    eq_(app.mepanel.amount_field.text, '0.00')

def test_change_field():
    # Changing a field enables the associated checkbox
    app = app_two_transactions_different_value()
    app.clear_gui_calls()
    app.mepanel.date_field.text = '08/07/2008'
    assert app.mepanel.date_enabled
    # just make sure they are not changed all at once
    assert not app.mepanel.description_enabled
    app.mepanel.view.check_gui_calls(['refresh'])
    app.mepanel.description_field.text = 'foobar'
    assert app.mepanel.description_enabled
    app.mepanel.view.check_gui_calls(['refresh'])
    app.mepanel.payee_field.text = 'foobar'
    assert app.mepanel.payee_enabled
    app.mepanel.view.check_gui_calls(['refresh'])
    app.mepanel.checkno_field.text = '44'
    assert app.mepanel.checkno_enabled
    app.mepanel.view.check_gui_calls(['refresh'])
    app.mepanel.from_field.text = 'foobar'
    assert app.mepanel.from_enabled
    app.mepanel.view.check_gui_calls(['refresh'])
    app.mepanel.to_field.text = 'foobar'
    assert app.mepanel.to_enabled
    app.mepanel.view.check_gui_calls(['refresh'])
    app.mepanel.amount_field.text = '44'
    assert app.mepanel.amount_enabled
    app.mepanel.view.check_gui_calls(['refresh'])

def test_change_field_to_none():
    # the mass panel considers replaces None values with ''.
    app = app_two_transactions_different_value()
    app.mepanel.description_field.text = None
    app.mepanel.payee_field.text = None
    app.mepanel.checkno_field.text = None
    app.mepanel.from_field.text = None
    app.mepanel.to_field.text = None
    app.mepanel.amount_field.text = None
    assert not app.mepanel.description_enabled
    assert not app.mepanel.payee_enabled
    assert not app.mepanel.checkno_enabled
    assert not app.mepanel.from_enabled
    assert not app.mepanel.to_enabled
    assert not app.mepanel.amount_enabled
    eq_(app.mepanel.description_field.text, '')
    eq_(app.mepanel.payee_field.text, '')
    eq_(app.mepanel.checkno_field.text, '')
    eq_(app.mepanel.from_field.text, '')
    eq_(app.mepanel.to_field.text, '')
    eq_(app.mepanel.amount_field.text, '0.00')

def test_change_and_save():
    # save() performs mass edits on selected transactions.
    app = app_two_transactions_different_value()
    app.save_file()
    app.mepanel.date_field.text = '08/07/2008'
    app.mepanel.description_field.text = 'description3'
    app.mepanel.payee_field.text = 'payee3'
    app.mepanel.checkno_field.text = '44'
    app.mepanel.from_field.text = 'from3'
    app.mepanel.to_field.text = 'to3'
    app.mepanel.amount_field.text = '44'
    app.mepanel.save()
    assert app.doc.is_dirty()
    for row in app.ttable.rows:
        eq_(row.date, '08/07/2008')
        eq_(row.description, 'description3')
        eq_(row.payee, 'payee3')
        eq_(row.checkno, '44')
        eq_(row.from_, 'from3')
        eq_(row.to, 'to3')
        eq_(row.amount, '44.00')

def test_change_date_only():
    # Only change checked fields.
    app = app_two_transactions_different_value()
    app.mepanel.date_field.text = '08/07/2008'
    app.mepanel.description_field.text = 'description3'
    app.mepanel.payee_field.text = 'payee3'
    app.mepanel.checkno_field.text = '44'
    app.mepanel.from_field.text = 'from3'
    app.mepanel.to_field.text = 'to3'
    app.mepanel.amount_field.text = '44'
    app.mepanel.description_enabled = False
    app.mepanel.payee_enabled = False
    app.mepanel.checkno_enabled = False
    app.mepanel.from_enabled = False
    app.mepanel.to_enabled = False
    app.mepanel.amount_enabled = False
    app.mepanel.save()
    row = app.ttable[0]
    eq_(row.date, '08/07/2008')
    eq_(row.description, 'description1')
    eq_(row.payee, 'payee1')
    eq_(row.checkno, '42')
    eq_(row.from_, 'from1')
    eq_(row.to, 'to1')
    eq_(row.amount, '42.00')

def test_change_description_only():
    # test_change_date_only is not enough for complete coverage.
    app = app_two_transactions_different_value()
    app.mepanel.date_field.text = '08/07/2008'
    app.mepanel.description_field.text = 'description3'
    app.mepanel.date_enabled = False
    app.mepanel.save()
    row = app.ttable[0]
    eq_(row.date, '06/07/2008')
    eq_(row.description, 'description3')

#--- Two transactions same values
def app_two_transactions_same_values():
    app = TestApp()
    app.add_account('account1')
    app.show_account()
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
    app.etable.select([0, 1])
    app.mepanel.load()
    return app

@with_app(app_two_transactions_same_values)
def test_attributes_when_same_values(app):
    # All fields are disabled but contain the values common to all selection.
    assert not app.mepanel.date_enabled
    assert not app.mepanel.description_enabled
    assert not app.mepanel.payee_enabled
    assert not app.mepanel.checkno_enabled
    assert not app.mepanel.from_enabled
    assert not app.mepanel.to_enabled
    assert not app.mepanel.amount_enabled
    eq_(app.mepanel.date_field.text, '06/07/2008')
    eq_(app.mepanel.description_field.text, 'description')
    eq_(app.mepanel.payee_field.text, 'payee')
    eq_(app.mepanel.checkno_field.text, '42')
    eq_(app.mepanel.from_field.text, 'account2')
    eq_(app.mepanel.to_field.text, 'account1')
    eq_(app.mepanel.amount_field.text, '42.00')

@with_app(app_two_transactions_same_values)
def test_change_field_same(app):
    # Don't auto-enable when changing a field to the same value.
    app.mepanel.date = '06/07/2008'
    assert not app.mepanel.date_enabled
    app.mepanel.description = 'description'
    assert not app.mepanel.description_enabled
    app.mepanel.payee = 'payee'
    assert not app.mepanel.payee_enabled
    app.mepanel.checkno = '42'
    assert not app.mepanel.checkno_enabled
    app.mepanel.from_ = 'account2'
    assert not app.mepanel.from_enabled
    app.mepanel.to = 'account1'
    assert not app.mepanel.to_enabled
    app.mepanel.amount = '42'
    assert not app.mepanel.amount_enabled

@with_app(app_two_transactions_same_values)
def test_load_again(app, monkeypatch):
    # load() blanks values when necessary.
    monkeypatch.patch_today(2010, 2, 20)
    app.mepanel.date_enabled = True
    app.mepanel.description_enabled = True
    app.mepanel.payee_enabled = True
    app.mepanel.checkno_enabled = True
    app.mepanel.from_enabled = True
    app.mepanel.amount_enabled = True
    app.add_entry(date='07/07/2008') # Now, none of the values are common
    app.etable.select([0, 1, 2])
    app.mepanel.load()
    assert not app.mepanel.date_enabled
    assert not app.mepanel.description_enabled
    assert not app.mepanel.payee_enabled
    assert not app.mepanel.checkno_enabled
    assert not app.mepanel.from_enabled
    assert not app.mepanel.to_enabled
    assert not app.mepanel.amount_enabled
    eq_(app.mepanel.date_field.text, '20/02/2010')
    eq_(app.mepanel.description_field.text, '')
    eq_(app.mepanel.payee_field.text, '')
    eq_(app.mepanel.checkno_field.text, '')

#--- Two transactions one split
def app_two_transactions_one_split():
    app = TestApp()
    app.add_account('account1')
    app.show_account()
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
    app.tpanel.load()
    app.stable.add()
    row = app.stable.selected_row
    row.account = 'account3'
    row.debit = '24'
    app.stable.save_edits()
    app.tpanel.save()
    app.etable.select([0, 1])
    app.mepanel.load()
    return app
    
def test_cant_change_accounts():
    app = app_two_transactions_one_split()
    assert not app.mepanel.can_change_accounts


#--- Two foreign transactions
def app_two_foreign_transactions():
    app = TestApp()
    app.add_account('account1')
    app.show_account()
    app.add_entry(increase='42 eur')
    app.add_entry(increase='42 eur')
    app.show_tview()
    app.ttable.select([0, 1])
    app.mepanel.load()
    return app

def test_amount_has_correct_currency():
    #The amount is shown with a currency code and the selected currency is the correct one
    app = app_two_foreign_transactions()
    eq_(app.mepanel.amount_field.text, 'EUR 42.00')
    eq_(app.mepanel.currency_list.selected_index, 1) # EUR

def test_change_currency():
    # It's possible to mass edit currency
    app = app_two_foreign_transactions()
    app.mepanel.currency_list.select(3) # CAD
    assert app.mepanel.currency_enabled
    app.mepanel.currency_list.select(-1)
    assert not app.mepanel.currency_enabled
    app.mepanel.currency_list.select(3) # CAD
    assert app.mepanel.currency_enabled
    app.mepanel.save()
    eq_(app.ttable[0].amount, 'CAD 42.00')
    eq_(app.ttable[1].amount, 'CAD 42.00')

#--- Two transactions with a multi-currency one
def app_two_transactions_with_a_multi_currency_one():
    app = TestApp()
    app.add_txn('20/02/2010')
    app.tpanel.load()
    app.stable[0].credit = '44 usd'
    app.stable.save_edits()
    app.stable.select([1])
    app.stable[1].debit = '42 cad'
    app.stable.save_edits()
    app.tpanel.save()
    app.add_txn('20/02/2010')
    app.ttable.select([0, 1])
    app.mepanel.load()
    return app

#--- Transactions with splits
def app_transactions_with_splits():
    app = TestApp()
    app.add_txn()
    splits = [
        ('foo', '', '20', ''),
        ('bar', '', '', '10'),
        ('baz', '', '', '10'),
    ]
    app.add_txn_with_splits(splits)
    app.ttable.select([0, 1])
    app.mepanel.load()
    return app

@with_app(app_transactions_with_splits)
def test_currency_change_on_splits(app):
    # currency mass change also work on split transactions. There would previously be a crash.
    app.mepanel.currency_list.select(2) # GBP
    app.mepanel.save() # no crash
    eq_(app.ttable[1].amount, 'GBP 20.00')

#---
def app_transactions_with_different_currencies():
    app = TestApp()
    app.add_txn(amount='42 eur')
    app.add_txn(amount='42 cad')
    app.ttable.select([0, 1])
    return app

@with_app(app_transactions_with_different_currencies)
def test_set_currency_to_native_one_when_we_cant_choose_one_from_selection(app):
    # There was a bug previously where the panel's currency could stay at -1, causing the mass panel
    # to change all currencies to XPF (the last currency in the currency list).
    app.mepanel.load()
    eq_(app.mepanel.currency_list.selected_index, 0) # USD

#--- Generators
def test_can_change_amount():
    def check(app, expected):
        eq_(app.mepanel.can_change_amount, expected)
    
    # Splits prevent the Amount field from being enabled
    app = app_two_transactions_one_split()
    yield check, app, False
    
    # If a MCT is selected, amount is not editable
    app = app_two_transactions_with_a_multi_currency_one()
    yield check, app, False
