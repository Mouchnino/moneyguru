# Created By: Virgil Dupras
# Created On: 2008-06-13
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from .base import TestApp, with_app

#--- Empty account
def app_empty_account():
    app = TestApp()
    app.add_account('Checking')
    app.mw.show_account()
    return app

@with_app(app_empty_account)
def test_add_entry_check_splits(app):
    # A newly added entry has its splits set.
    # Previously, split_count() would be zero until a save_entry()
    app.etable.add()
    app.tpanel.load()
    eq_(len(app.stable), 2)
    eq_(app.stable[0].account, 'Checking')
    eq_(app.stable[0].debit, '')
    eq_(app.stable[0].credit, '')
    eq_(app.stable[1].account, '')
    eq_(app.stable[1].debit, '')
    eq_(app.stable[1].credit, '')

@with_app(app_empty_account)
def test_add_entry_save_split(app):
    # Saving a split in a newly added entry doesn't make it disappear.
    # Previously, saving splits to a newly created entry would make it disappear because the
    # cooking would be made before the transaction could be added
    app.etable.add()
    app.tpanel.load()
    app.stable.add()
    app.stable.save_edits()
    app.tpanel.save()
    eq_(app.etable_count(), 1)

#--- One entry
def app_one_entry():
    app = TestApp()
    app.add_account('Checking')
    app.mw.show_account()
    app.add_entry('10/10/2007', 'Deposit', transfer='Salary', increase='42.00')
    return app

@with_app(app_one_entry)
def test_save_split_on_second_row(app):
    # save_split() doesn't change the selected row.
    app.tpanel.load()
    app.stable.select([1])
    row = app.stable.selected_row
    row.account = 'foobar'
    app.stable.save_edits()
    eq_(app.stable.selected_index, 1)

@with_app(app_one_entry)
def test_split_are_correctly_assigned(app):
    # There are two splits and the attributes are correct.
    app.tpanel.load()
    eq_(len(app.stable), 2)
    eq_(app.stable[0].account, 'Checking')
    eq_(app.stable[0].debit, '42.00')
    eq_(app.stable[1].account, 'Salary')
    eq_(app.stable[1].credit, '42.00')

@with_app(app_one_entry)
def test_set_split_credit(app):
    # Setting the split credit changes the split credit, the entry amount and the balance.
    app.tpanel.load()
    row = app.stable.selected_row
    row.credit = '100.00'
    app.stable.save_edits()
    app.tpanel.save()
    eq_(app.stable[0].credit, '100.00')
    eq_(app.etable[0].decrease, '100.00')
    eq_(app.etable[0].balance, '-100.00')

@with_app(app_one_entry)
def test_set_split_debit(app):
    # Setting the split debit changes the split debit, the entry amount and the balance.
    app.tpanel.load()
    row = app.stable.selected_row
    row.debit = '100.00'
    app.stable.save_edits()
    app.tpanel.save()
    eq_(app.stable[0].debit, '100.00')
    eq_(app.etable[0].increase, '100.00')
    eq_(app.etable[0].balance, '100.00')

@with_app(app_one_entry)
def test_set_split_account(app):
    # Setting the split account changes both the split and the entry. If the current entry's account
    # is changed, the account selection changes too.
    app.tpanel.load()
    row = app.stable.selected_row
    row.account = 'foo'
    app.stable.save_edits()
    app.tpanel.save()
    app.mw.select_balance_sheet()
    eq_(app.bsheet.assets[1].name, 'foo') # The foo account was autocreated
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.show_selected_account()
    app.tpanel.load()
    app.stable.select([1])
    row = app.stable.selected_row
    row.account = 'bar'
    app.stable.save_edits()
    app.tpanel.save()
    eq_(app.stable[1].account, 'bar')
    eq_(app.etable[0].transfer, 'bar')
    app.mw.select_income_statement()
    eq_(app.istatement.income[0].name, 'bar') # The bar account was autocreated

#--- Entry without transfer
def app_entry_without_transfer():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry(description='foobar', decrease='130.00')
    return app

@with_app(app_entry_without_transfer)
def test_split_has_unassigned_account(app):
    # There are two splits and their amounts and accounts are correct.
    app.tpanel.load()
    eq_(len(app.stable), 2)
    eq_(app.stable[0].account, 'New account')
    eq_(app.stable[0].credit, '130.00')
    eq_(app.stable[1].account, '')
    eq_(app.stable[1].debit, '130.00')

#--- Split transaction
def app_split_transaction():
    # New Account   0 100
    # expense1    100   0
    # expense2     10   0
    # income        0   1
    # Unassigned    0   9
    app = TestApp()
    app.add_account('New Account')
    splits = [
        ('New Account', '', '', '100'),
        ('expense1', '', '100', ''),
        ('expense2', '', '10', ''),
        ('income', '', '', '1'),
    ] # there will be an unassigned for 9
    app.add_txn_with_splits(splits, date='2/1/2007', description='Split')
    app.show_account('New Account')
    app.add_entry(date='3/1/2007')   # That's to make sure the selection doesn't change on edits
    app.etable.select([0])
    return app

@with_app(app_split_transaction)
def test_amounts(app):
    # All split amounts are right.
    app.tpanel.load()
    eq_(app.stable[0].credit, '100.00')
    eq_(app.stable[1].debit, '100.00')
    eq_(app.stable[2].debit, '10.00')
    eq_(app.stable[3].credit, '1.00')
    eq_(app.stable[4].credit, '9.00')
    eq_(app.etable[0].decrease, '100.00')

@with_app(app_split_transaction)
def test_delete_split(app):
    # Deleting a split works.
    app.tpanel.load()
    app.stable.select([2])
    app.stable.delete()
    eq_(len(app.stable), 4)
    # The unassigned split took the difference
    eq_(app.stable[2].account, 'income')
    eq_(app.stable[2].credit, '1.00')
    eq_(app.stable[3].debit, '1.00')

@with_app(app_split_transaction)
def test_revert_split(app):
    # Reverting the edits works.
    app.tpanel.load()
    row = app.stable.selected_row
    row.account = 'changed'
    row.debit = '2'
    app.stable.cancel_edits()
    eq_(app.stable[3].account, 'income')
    eq_(app.stable[3].credit, '1.00')

@with_app(app_split_transaction)
def test_save_entry(app):
    # Saving an entry doesn't change the amounts.
    row = app.etable.selected_row
    row.description = 'Another description'
    app.etable.save_edits()
    app.tpanel.load()
    eq_(len(app.stable), 5)
    eq_(app.stable[0].credit, '100.00')
    eq_(app.stable[1].debit, '100.00')
    eq_(app.stable[2].debit, '10.00')
    eq_(app.stable[3].credit, '1.00')
    eq_(app.stable[4].credit, '9.00')

@with_app(app_split_transaction)
def test_select_another_entry(app):
    # Selecting another entry resets the split index to 0.
    app.etable.select([1])
    app.tpanel.load()
    eq_(app.stable.selected_index, 0)

@with_app(app_split_transaction)
def test_split_count(app):
    # All splits are shown.
    app.tpanel.load()
    eq_(len(app.stable), 5)

@with_app(app_split_transaction)
def test_transfer_read_only(app):
    # The transfer column shows a list of affecter *other* accounts and is read-only.
    eq_(app.etable[0].transfer, 'expense1, expense2, income')
    assert not app.etable.can_edit_cell('transfer', 0)

#--- Split with no account
def app_split_with_no_account():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry(date='2/1/2007', description='Split', transfer='expense1', decrease='100')
    app.tpanel.load()
    app.stable.add()
    row = app.stable.selected_row
    row.credit = '10'
    app.stable.save_edits()
    app.tpanel.save()
    return app

@with_app(app_split_with_no_account)
def test_transfer_doesnt_include_unassigned_split(app):
    # The transfer column don't include splits with no account.
    eq_(app.etable[0].transfer, 'expense1')
