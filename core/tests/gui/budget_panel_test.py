# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-08-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_
from hsutil.testutil import Patcher

from ...model.account import AccountType
from ..base import TestApp, with_app

#--- One asset account
def app_one_asset_account():
    app = TestApp()
    app.add_account('asset')
    app.mainwindow.show_account()
    return app

def test_can_create_new():
    # When trying to create a new budget in a document without income/expense accounts, an
    # error message is displayed explaining that it's not possible.
    app = app_one_asset_account()
    app.mainwindow.select_budget_table()
    app.mainwindow.new_item()
    eq_(len(app.mainwindow_gui.messages), 1) # a message has been shown

#--- One expense with budget
def app_one_expense_with_budget():
    p = Patcher()
    p.patch_today(2008, 1, 27)
    app = TestApp()
    app.drsel.select_today_date_range()
    app.add_account('Some Expense', account_type=AccountType.Expense)
    app.add_budget('Some Expense', None, '100')
    app.mainwindow.select_income_statement()
    # The accounts' name and order in which they are created is important, as it tests that
    # the budget panel sorts them correctly.
    app.add_account('liability', account_type=AccountType.Liability)
    app.add_account('asset')
    app.add_account('Some Income', account_type=AccountType.Income)
    app.mainwindow.select_budget_table()
    app.btable.select([0])
    app.mainwindow.edit_item()
    return app, p

@with_app(app_one_expense_with_budget)
def test_attrs(app):
    eq_(app.bpanel.start_date, '01/01/2008')
    eq_(app.bpanel.stop_date, '')
    eq_(app.bpanel.repeat_type_index, 2) # monthly
    eq_(app.bpanel.repeat_every, 1)
    eq_(app.bpanel.account_options, ['Some Income', 'Some Expense'])
    eq_(app.bpanel.account_index, 1)
    eq_(app.bpanel.target_options, ['None', 'asset', 'liability'])
    eq_(app.bpanel.target_index, 0)
    eq_(app.bpanel.amount, '100.00')

@with_app(app_one_expense_with_budget)
def test_edit_then_save(app):
    # Saving edits on the panel actually updates the budget
    app.bpanel.account_index = 0 # Some Income
    app.bpanel.target_index = 2 # liability
    app.bpanel.amount = '42'
    app.bpanel.notes = 'foobar'
    app.bpanel.save()
    # Set new values without saving
    app.bpanel.amount = '43'
    app.bpanel.notes = 'foobaz'
    # Reload the panel and check the values
    app.mainwindow.edit_item()
    eq_(app.bpanel.amount, '42.00')
    eq_(app.bpanel.notes, 'foobar')
    # Check that the correct info is in the btable.
    row = app.btable[0]
    eq_(row.account, 'Some Income')
    eq_(row.target, 'liability')
    eq_(row.amount, '42.00')
    # To see if the save_edits() worked, we look if the spawns are correct in the ttable
    app.mainwindow.select_transaction_table()
    row = app.ttable[0]
    eq_(row.to, 'liability')
    eq_(row.from_, 'Some Income')
    eq_(row.amount, '42.00')

@with_app(app_one_expense_with_budget)
def test_edit_without_selection(app):
    # Initiating a budget edition while none is selected doesn't crash
    app.btable.select([])
    app.mainwindow.edit_item() # no crash

@with_app(app_one_expense_with_budget)
def test_new_budget(app):
    app.mainwindow.new_item()
    eq_(app.bpanel.start_date, '27/01/2008') # mocked date
    eq_(app.bpanel.repeat_type_index, 2) # monthly
    eq_(app.bpanel.account_index, 0)
    eq_(app.bpanel.target_index, 0)
    app.bpanel.save()
    eq_(len(app.btable), 2) # has been added
