# Created By: Virgil Dupras
# Created On: 2009-08-23
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

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
    app.show_bview()
    app.mainwindow.new_item()
    eq_(len(app.mainwindow_gui.messages), 1) # a message has been shown

#--- One expense with budget
def app_one_expense_with_budget(monkeypatch):
    monkeypatch.patch_today(2008, 1, 27)
    app = TestApp()
    app.drsel.select_today_date_range()
    app.add_account('Some Expense', account_type=AccountType.Expense)
    app.add_budget('Some Expense', None, '100')
    app.show_pview()
    # The accounts' name and order in which they are created is important, as it tests that
    # the budget panel sorts them correctly.
    app.add_account('liability', account_type=AccountType.Liability)
    app.add_account('asset')
    app.add_account('Some Income', account_type=AccountType.Income)
    app.show_bview()
    app.btable.select([0])
    app.mainwindow.edit_item()
    return app

@with_app(app_one_expense_with_budget)
def test_attrs(app):
    eq_(app.bpanel.start_date, '01/01/2008')
    eq_(app.bpanel.stop_date, '')
    eq_(app.bpanel.repeat_type_list.selected_index, 2) # monthly
    eq_(app.bpanel.repeat_every, 1)
    eq_(app.bpanel.account_list[:], ['Some Income', 'Some Expense'])
    eq_(app.bpanel.account_list.selected_index, 1)
    eq_(app.bpanel.target_list[:], ['None', 'asset', 'liability'])
    eq_(app.bpanel.target_list.selected_index, 0)
    eq_(app.bpanel.amount, '100.00')

@with_app(app_one_expense_with_budget)
def test_edit_then_save(app):
    # Saving edits on the panel actually updates the budget
    app.bpanel.account_list.select(0) # Some Income
    app.bpanel.target_list.select(2) # liability
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
    app.show_tview()
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
    eq_(app.bpanel.repeat_type_list.selected_index, 2) # monthly
    eq_(app.bpanel.account_list.selected_index, 0)
    eq_(app.bpanel.target_list.selected_index, 0)
    app.bpanel.save()
    eq_(len(app.btable), 2) # has been added
