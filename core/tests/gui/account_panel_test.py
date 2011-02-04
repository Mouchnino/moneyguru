# Created By: Virgil Dupras
# Created On: 2008-07-03
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_
from hscommon.currency import Currency, CAD

from ..base import TestApp, with_app
from ...model.account import AccountType

#--- Some account
def app_some_account():
    app = TestApp()
    app.add_account('foobar', CAD, account_type=AccountType.Expense, account_number='4242')
    app.mw.select_income_statement()
    app.clear_gui_calls()
    return app

@with_app(app_some_account)
def test_change_currency_index(app):
    # Changing currency_index correctly updates the currency.
    app.apanel.currency_index = 0
    eq_(app.apanel.currency, Currency.all[0])
    app.apanel.currency_index = 42
    eq_(app.apanel.currency, Currency.all[42])
    app.apanel.currency_index = 9999 # doesn't do anything
    eq_(app.apanel.currency, Currency.all[42])
    eq_(app.apanel.currency_index, 42)

@with_app(app_some_account)
def test_change_type_index(app):
    # Changing type_index correctly updates the type.
    app.apanel.type_index = 0
    eq_(app.apanel.type, AccountType.Asset)
    app.apanel.type_index = 1
    eq_(app.apanel.type, AccountType.Liability)
    app.apanel.type_index = 2
    eq_(app.apanel.type, AccountType.Income)
    app.apanel.type_index = 4 # doesn't do anything
    eq_(app.apanel.type, AccountType.Income)
    eq_(app.apanel.type_index, 2)

@with_app(app_some_account)
def test_fields(app):
    # The base field values.
    app.mw.edit_item()
    eq_(app.apanel.name, 'foobar')
    eq_(app.apanel.type, AccountType.Expense)
    eq_(app.apanel.currency, CAD)
    eq_(app.apanel.type_index, 3) # Expense type is last in the list
    eq_(app.apanel.currency_index, Currency.all.index(CAD))
    eq_(app.apanel.account_number, '4242')
    eq_(app.apanel.notes, '')

@with_app(app_some_account)
def test_fields_before_load(app):
    # ensure no crash occurs
    app.apanel.type_index

@with_app(app_some_account)
def test_load_stops_edition(app):
    # edition must be stop on apanel load or else an account type change can result in a crash
    app.mw.edit_item()
    app.check_gui_calls(app.istatement_gui, ['stop_editing'])

#--- Two accounts
def app_two_accounts():
    app = TestApp()
    app.add_account('foobar')
    app.add_account('foobaz')
    app.clear_gui_calls()
    return app

@with_app(app_two_accounts)
def test_duplicate_name(app):
    # setting a duplicate account name makes the dialog show a warning label
    app.mw.edit_item()
    app.apanel.name = 'foobar'
    app.apanel.save() # the exception doesn't propagate

@with_app(app_two_accounts)
def test_save_then_load(app):
    # save() calls document.change_account with the correct arguments and triggers a refresh on
    # all GUI components. We have to test this on two accounts to make sure that the values we test
    # on load aren't just leftovers from past assignments
    app.mw.edit_item() # foobaz
    app.apanel.type_index = 1
    app.apanel.currency_index = 42
    app.apanel.name = 'changed name'
    app.apanel.account_number = '4241'
    app.apanel.notes = 'some notes'
    app.apanel.save()
    app.bsheet.selected = app.bsheet.assets[0] # foobar
    app.mw.edit_item()
    app.apanel.type_index = 0
    app.apanel.currency_index = 0
    app.apanel.name = 'whatever'
    app.apanel.account_number = '1234'
    app.apanel.notes = 'other notes'
    app.apanel.save()
    # To test the currency, we have to load again
    app.bsheet.selected = app.bsheet.liabilities[0] # foobaz
    app.mw.edit_item()
    eq_(app.apanel.currency, Currency.all[42])
    eq_(app.apanel.type, AccountType.Liability)
    eq_(app.apanel.name, 'changed name')
    eq_(app.apanel.account_number, '4241')
    eq_(app.apanel.notes, 'some notes')