# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from pytest import raises
from hscommon.testutil import eq_
from hscommon.currency import USD

from ...exception import OperationAborted
from ..base import TestApp, with_app

#--- Pristine
def test_attrs():
    # No crash occur when trying to access atrtibutes while the panel is not loaded
    app = TestApp()
    app.tpanel.date # No crash

def test_can_load():
    # When there's no selection, loading the panel raises OperationAborted
    app = TestApp()
    with raises(OperationAborted):
        app.tpanel.load()

#--- One Entry
def app_one_entry():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42')
    return app

def test_add_cancel_then_load():
    # when loading the tpanel right after cancelling a txn addition, the wrong txn is loaded
    app = app_one_entry()
    app.etable.add()
    app.etable.cancel_edits()
    app.tpanel.load()
    eq_(app.tpanel.description, 'description')

def test_buffer():
    # tpanel's edition is buffered.
    app = app_one_entry()
    app.tpanel.load()
    app.tpanel.date = '07/07/2008'
    app.tpanel.description = 'foo'
    app.tpanel.payee = 'bar'
    app.tpanel.checkno = 'baz'
    app.tpanel.load()
    eq_(app.tpanel.date, '06/07/2008')
    eq_(app.tpanel.description, 'description')
    eq_(app.tpanel.payee, 'payee')
    eq_(app.tpanel.checkno, '42')

def test_can_load_selected_transaction():
    # Whether load() is possible is based on the last selection of either the etable or the ttable
    app = app_one_entry()
    app.etable.select([])
    app.mainwindow.select_transaction_table()
    app.ttable.select([0])
    app.tpanel.load() # no OperationAborted

def test_load_refreshes_mct_button():
    # loading the panel refreshes the mct button
    app = app_one_entry()
    app.tpanel.load()
    app.check_gui_calls_partial(app.tpanel_gui, ['refresh_for_multi_currency'])

def test_load_while_etable_is_editing():
    # loading the tpanel while etable is editing saves the edits and stops editing mode.
    app = app_one_entry()
    app.etable.add()
    row = app.etable.edited
    row.date = '07/07/2008'
    app.clear_gui_calls()
    app.tpanel.load()
    assert app.etable.edited is None
    eq_(app.etable_count(), 2)
    app.check_gui_calls(app.etable_gui, ['refresh', 'show_selected_row', 'stop_editing'])

def test_load_while_ttable_is_editing():
    # loading the tpanel while ttable is editing saves the edits and stops editing mode.
    app = app_one_entry()
    app.mainwindow.select_transaction_table()
    app.ttable.add()
    row = app.ttable.edited
    row.date = '07/07/2008'
    app.clear_gui_calls()
    app.tpanel.load()
    assert app.ttable.edited is None
    eq_(app.ttable.row_count, 2)
    app.check_gui_calls(app.ttable_gui, ['refresh', 'show_selected_row', 'stop_editing'])

def test_values():
    # The values of the panel are correct.
    app = app_one_entry()
    app.tpanel.load() # no OperationAborted
    eq_(app.tpanel.date, '06/07/2008')
    eq_(app.tpanel.description, 'description')
    eq_(app.tpanel.payee, 'payee')
    eq_(app.tpanel.checkno, '42')

def test_values_after_deselect():
    # When there is no selection, load() is not possible
    app = app_one_entry()
    app.etable.select([])
    with raises(OperationAborted):
        app.tpanel.load()

#--- Amountless Entry Panel Loaded
def app_amountless_entry_panel_loaded():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42')
    app.mainwindow.select_transaction_table()
    app.ttable.select([0])
    app.tpanel.load()
    app.clear_gui_calls()
    return app

#--- Entry With Amount Panel Loaded
def app_entry_with_amount_panel_loaded():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry(date='06/07/2008', description='description', increase='42')
    app.mainwindow.select_transaction_table()
    app.ttable.select([0])
    app.tpanel.load()
    app.clear_gui_calls()
    return app

def test_change_date():
    # Changing the date no longer calls refresh_repeat_options() on the view (this stuff is now
    # in schedules)
    app = app_entry_with_amount_panel_loaded()
    app.tpanel.date = '17/07/2008'
    app.check_gui_calls_partial(app.tpanel_gui, not_expected=['refresh_repeat_options'])

#--- Two Amountless Entries
def app_two_amountless_entries():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry(date='06/07/2008', description='desc1', payee='payee1', checkno='42')
    app.add_entry(date='07/07/2008', description='desc2', payee='payee2', checkno='43')
    return app

def test_loads_last_selected_transaction():
    # the tpanel also works with the ttable. If the ttable is the last to have had a selection,
    # tpanel loads this one.
    app = app_two_amountless_entries()
    app.mainwindow.select_transaction_table()
    app.ttable.select([0]) # etable has index 1 selected
    app.tpanel.load()
    eq_(app.tpanel.description, 'desc1')

def test_set_values():
    # the load/save mechanism works for all attributes.
    # The reason why we select another entry is to make sure that the value we're testing isn't
    # simply a buffer in the gui layer.
    app = app_two_amountless_entries()
    
    def set_and_test(attrname, newvalue, othervalue):
        app.tpanel.load()
        setattr(app.tpanel, attrname, newvalue)
        app.tpanel.save()
        app.etable.select([0])
        app.tpanel.load()
        eq_(getattr(app.tpanel, attrname), othervalue)
        app.etable.select([1])
        app.tpanel.load()
        eq_(getattr(app.tpanel, attrname), newvalue)
    
    yield set_and_test, 'date', '08/07/2008', '06/07/2008'
    yield set_and_test, 'description', 'new', 'desc1'
    yield set_and_test, 'payee', 'new', 'payee1'
    yield set_and_test, 'checkno', '44', '42'
    yield set_and_test, 'notes', 'foo\nbar', ''

#--- Multi-Currency Transaction
def app_multi_currency_transaction():
    app = TestApp()
    USD.set_CAD_value(0.8, date(2008, 1, 1))
    splits = [
        ('first', '', '', '44 usd'),
        ('second', '', '42 cad', ''),
    ]
    app.add_txn_with_splits(splits)
    app.mw.edit_item()
    app.stable.select([1])
    app.clear_gui_calls()
    return app

def test_mct_balance():
    # a mct balance takes the "lowest side" of the transaction and adds a split with the
    # difference on that side. For this example, the usd side is the weakest side (if they were
    # equal, it would be 52.50 usd).
    app = app_multi_currency_transaction()
    app.tpanel.mct_balance()
    eq_(len(app.stable), 3)
    eq_(app.stable[2].credit, 'CAD 6.80') # the selected split is the 2nd one
    app.stable.view.check_gui_calls_partial(['refresh', 'stop_editing'])

@with_app(app_multi_currency_transaction)
def test_mct_balance_reuses_unassigned_split(app):
    # mct balance reuses unassigned split if available
    app.stable.add()
    app.stable[2].credit = '1 cad'
    app.stable.save_edits()
    app.tpanel.mct_balance()
    eq_(len(app.stable), 3)
    eq_(app.stable[2].credit, 'CAD 6.80')

def test_mct_balance_select_null_split():
    # if the selected split has no amount, use the default currency
    app = app_multi_currency_transaction()
    app.stable.add()
    app.tpanel.mct_balance()
    eq_(app.stable[2].credit, '8.50') # the newly added split is re-used

def test_mct_balance_select_usd_split():
    # the currency of the new split is the currency of the selected split
    app = app_multi_currency_transaction()
    app.stable.select([0])
    app.tpanel.mct_balance()
    eq_(app.stable[2].credit, '8.50')

def test_mct_balance_twice():
    # if there is nothing to balance, don't add anything.
    app = app_multi_currency_transaction()
    app.tpanel.mct_balance()
    app.tpanel.mct_balance()
    eq_(len(app.stable), 3)

def test_stop_edition_on_mct_balance():
    # edition must stop before mct balance or else we end up with a crash
    app = app_multi_currency_transaction()
    app.stable[1].account = 'foo'
    app.tpanel.mct_balance()
    app.stable.view.check_gui_calls_partial(['stop_editing'])

#--- Generators (tests with more than one setup)
def test_is_multi_currency():
    def check(setupfunc, expected):
        app = setupfunc()
        eq_(app.tpanel.is_multi_currency, expected)
    
    # doesn't crash if there is no split with amounts
    yield check, app_amountless_entry_panel_loaded, False
    # the mct balance button is enabled if the txn is a MCT
    yield check, app_entry_with_amount_panel_loaded, False
    # the mct balance button is enabled if the txn is a MCT
    yield check, app_multi_currency_transaction, True
