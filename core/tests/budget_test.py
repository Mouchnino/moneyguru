# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-06-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from hsutil.testutil import Patcher

from ..model.account import AccountType
from .base import TestApp, with_app

#-- Account with budget
def app_account_with_budget():
    # 4 days left to the month, 100$ monthly budget
    p = Patcher()
    p.patch_today(2008, 1, 27)
    app = TestApp()
    app.add_account('Some Income', account_type=AccountType.Income)
    app.add_budget('Some Income', None, '100')
    return app, p

@with_app(app_account_with_budget)
def test_budget_amount_flow_direction(app):
    # When the budgeted account is an income, the account gets in the *from* column
    app.mw.select_transaction_table()
    eq_(app.ttable[0].from_, 'Some Income')

@with_app(app_account_with_budget)
def test_dont_replace_split_instances_needlessly(app):
    # The bug was that during budget cooking, all spawns, including those before the cooked date
    # range, would have their split re-created with new amounts. Because of this, going back in
    # the date range would cause cached entries to be "bumped out" of the transaction. This
    # would result in the shown account to be displayed in the "Transfer" column.
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[0]
    app.istatement.show_selected_account()
    eq_(app.etable[0].transfer, '')
    app.drsel.select_next_date_range()
    app.drsel.select_prev_date_range()
    eq_(app.etable[0].transfer, '') # It shouldn't be set to "Some Income"

@with_app(app_account_with_budget)
def test_save_and_load(app):
    # There was a crash when loading a targetless budget
    newapp = app.save_and_load() # no crash
    newapp.mw.select_budget_table()
    eq_(len(newapp.btable), 1)

@with_app(app_account_with_budget)
def test_set_budget_again(app):
    # There was a bug where setting the amount on a budget again wouldn't invert that amount
    # in the case of an income-based budget.
    app.mw.select_budget_table()
    app.btable.select([0])
    app.mw.edit_item()
    app.bpanel.amount = '200'
    app.bpanel.save()
    app.mw.select_transaction_table()
    eq_(app.ttable[0].from_, 'Some Income')

#--- Income with budget in past
def app_income_with_budget_in_past():
    p = Patcher()
    p.patch_today(2009, 11, 16)
    app = TestApp()
    app.add_account('income', account_type=AccountType.Income)
    app.add_budget('income', None, '100', start_date='01/09/2009')
    return app, p

@with_app(app_income_with_budget_in_past)
def test_spawns_dont_linger(app):
    # If the budget hasn't been spent in the past, we don't continue to spawn transactions for
    # it once we went past the spawn's end date.
    app.mw.select_transaction_table()
     # Only the spawns for november and december, NOT, september and october.
    eq_(app.ttable.row_count, 2)

#--- Expense with budget and txn
def app_budget_with_expense_and_txn():
    p = Patcher()
    p.patch_today(2008, 1, 27)
    app = TestApp()
    app.add_account('Some Expense', account_type=AccountType.Expense)
    app.add_budget('Some Expense', None, '100')
    app.add_txn(date='27/01/2008', to='Some Expense', amount='42')
    return app, p

@with_app(app_budget_with_expense_and_txn)
def test_budget_transaction_is_adjusted(app):
    # Adding a transaction affects the next budget transaction
    eq_(app.ttable[1].amount, '58.00')
    eq_(app.ttable[2].amount, '100.00')

@with_app(app_budget_with_expense_and_txn)
def test_busted_budget_spaws_dont_show_up(app):
    # When a budget is busted, don't show the spawn
    app.ttable[0].amount = '142'
    app.ttable.save_edits()
    eq_(app.ttable.row_count, 12)
    eq_(app.ttable[1].date, '29/02/2008')
    

#--- Expense with budget and target
def app_expense_with_budget_and_target():
    p = Patcher()
    p.patch_today(2008, 1, 27)
    app = TestApp()
    app.add_account('some asset')
    app.add_account('Some Expense', account_type=AccountType.Expense)
    app.add_budget('Some Expense', 'some asset', '100')
    return app, p

@with_app(app_expense_with_budget_and_target)
def test_asset_is_in_the_from_column(app):
    # In the budget transaction, 'some asset' is in the 'from' column.
    app.mw.select_transaction_table()
    eq_(app.ttable[0].from_, 'some asset')

@with_app(app_expense_with_budget_and_target)
def test_budget_is_counted_in_etable_balance(app):
    # When an asset is a budget target, its balance is correctly incremented in the etable.
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    # The balance of the budget entry has a correctly decremented balance (the budget is an expense).
    eq_(app.etable[0].balance, '-100.00')

@with_app(app_expense_with_budget_and_target)
def test_delete_account(app):
    # When deleting an income or expense account, delete all budgets associated with it as well.
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.expenses[0]
    app.istatement.delete()
    app.arpanel.save() # don't reassign
    app.mw.select_budget_table()
    eq_(len(app.btable), 0) # the budget has been removed

@with_app(app_expense_with_budget_and_target)
def test_delete_account_and_reassign(app):
    # When reassigning an account on deletion, change budgets instead of deleting it.
    app.add_account('other expense', account_type=AccountType.Expense)
    app.istatement.selected = app.istatement.expenses[1] # Some Expense
    app.istatement.delete()
    app.arpanel.account_index = 2 # other expense
    app.arpanel.save()
    app.mw.select_budget_table()
    eq_(app.btable[0].account, 'other expense')

@with_app(app_expense_with_budget_and_target)
def test_delete_target(app):
    # When deleting the target account, budgets having this account as their target have it
    # changed to None
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    app.arpanel.save()
    app.mw.select_budget_table()
    eq_(app.btable[0].target, '') # been changed to None

@with_app(app_expense_with_budget_and_target)
def test_delete_target_and_reassign(app):
    # When reassigning an account on deletion, change budgets' target.
    app.add_account('other asset')
    app.bsheet.selected = app.bsheet.assets[1] # some asset
    app.bsheet.delete()
    app.arpanel.account_index = 1 # other asset
    app.arpanel.save()
    app.mw.select_budget_table()
    eq_(app.btable[0].target, 'other asset')

#--- Two budgets from same account
def app_two_budgets_from_same_account():
    # XXX this mock is because the test previously failed because we were currently on the last
    # day of the month. TODO: Re-create the last-day condition and fix the calculation bug
    p = Patcher()
    p.patch_today(2009, 8, 20)
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('income', account_type=AccountType.Income)
    app.add_txn(from_='income', amount='25') # This txn must not be counted twice in budget calculations!
    app.add_budget('income', None, '100')
    app.add_budget('income', None, '100')
    return app, p

@with_app(app_two_budgets_from_same_account)
def test_both_budgets_are_counted(app):
    # The amount budgeted is the sum of all budgets, not just the first one.
    app.mw.select_income_statement()
    eq_(app.istatement.income[0].budgeted, '175.00')

#--- Yearly buget with txn before current month
def app_yearly_budget_with_txn_before_current_month():
    p = Patcher()
    p.patch_today(2009, 8, 24)
    app = TestApp()
    app.drsel.select_year_range()
    app.add_account('income', account_type=AccountType.Income)
    app.add_txn(date='01/07/2009', from_='income', amount='25')
    app.add_budget('income', None, '100', start_date='01/01/2009', repeat_type_index=3) # yearly
    return app, p

@with_app(app_yearly_budget_with_txn_before_current_month)
def test_entry_is_correctly_counted_in_budget(app):
    # The entry, although not in the current month, is counted in budget calculations
    app.mw.select_income_statement()
    eq_(app.istatement.income[0].budgeted, '75.00')

@with_app(app_yearly_budget_with_txn_before_current_month)
def test_spawn_has_correct_date(app):
    # The spawn is created at the correct date, which is at the end of the year
    app.mw.select_transaction_table()
    # first txn is the entry on 01/07
    eq_(app.ttable[1].date, '31/12/2009')

#--- Scheduled txn and budget
def app_scheduled_txn_and_budget():
    p = Patcher()
    p.patch_today(2009, 9, 10)
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('account', account_type=AccountType.Expense)
    app.add_schedule(start_date='10/09/2009', account='account', amount='1', repeat_type_index=2) # monthly
    app.add_budget('account', None, '10') # monthly
    return app, p

@with_app(app_scheduled_txn_and_budget)
def test_schedule_affects_budget(app):
    # schedule spawns affect the budget spawns
    app.mw.select_transaction_table()
    eq_(app.ttable[1].amount, '9.00') # 1$ has been removed from the budgeted 10
