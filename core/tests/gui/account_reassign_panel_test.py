# Created By: Virgil Dupras
# Created On: 2009-04-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from hscommon.currency import USD, EUR

from ..base import TestApp, with_app

#--- Deleting second account
def app_deleting_second_account():
    app = TestApp()
    app.add_accounts('one', 'two')
    app.mw.show_account()
    app.add_entry(transfer='three', increase='42')
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[1] # account 'two', the one with the entry
    app.bsheet.delete() # the panel shows up
    return app

@with_app(app_deleting_second_account)
def test_available_accounts(app):
    # the available accounts in arpanel are No Account, one and three
    expected = ['No Account', 'one', 'three']
    eq_(app.arpanel.available_accounts, expected)

@with_app(app_deleting_second_account)
def test_no_delete_took_place(app):
    # the panel shows up, but no deletion takes place yet.
    eq_(len(app.bsheet.assets), 4) # 2 + total lines.

@with_app(app_deleting_second_account)
def test_reassign_to_one(app):
    # choosing 'one' and continuing reassigns two's entry to one.
    app.arpanel.account_index = 1 # one
    app.arpanel.save()
    eq_(len(app.bsheet.assets), 3) # now, it's deleted
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    eq_(app.etable_count(), 1)
    eq_(app.etable[0].transfer, 'three')
    eq_(app.etable[0].increase, '42.00') # got the right side of the txn

#--- Different currencies
def app_different_currencies_reconciled_entries():
    app = TestApp()
    app.add_account('one', currency=USD)
    app.add_account('two', currency=EUR)
    app.add_txn(description='txn 1', from_='one', amount='1 USD')
    app.add_txn(description='txn 2', from_='two', amount='1 EUR')
    app.show_account('one')
    app.aview.toggle_reconciliation_mode()
    app.etable[0].toggle_reconciled()
    app.aview.toggle_reconciliation_mode()
    app.show_account('two')
    app.aview.toggle_reconciliation_mode()
    app.etable[0].toggle_reconciled()
    app.aview.toggle_reconciliation_mode()
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[1] # account 'two', the one with the entry
    app.bsheet.delete() # the panel shows up
    return app

@with_app(app_different_currencies_reconciled_entries)
def test_reassign_to_account_with_different_currency(app):
    # When re-assigning transactions to a different account, de-reconcile them if the account is
    # of a different currency or else we get a crash when we compute the balance.
    app.arpanel.account_index = 1 # one
    app.arpanel.save() # no crash
    app.show_account('one')
    eq_(app.etable_count(), 2)
