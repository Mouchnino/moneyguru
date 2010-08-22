# Created By: Virgil Dupras
# Created On: 2008-07-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from ...const import PaneType
from ..base import TestApp, with_app

#--- Pristine
@with_app(TestApp)    
def test_set_query(app):
    # Setting the 'query' property works"""
    app.sfield.query = 'foobar'
    eq_(app.sfield.query, 'foobar')

@with_app(TestApp)    
def test_set_query_selects_transaction_pane(app):
    # Setting the search query selects the transaction tab specifically. Previously, the tab that
    # was selected was always the 3rd one, regardless of the type.
    app.mw.close_pane(2) # we close the transactions pane
    app.sfield.query = 'foo'
    app.check_current_pane(PaneType.Transaction)

#--- Two transactions
def app_two_transactions():
    app = TestApp()
    app.add_account('Desjardins')
    app.mw.show_account()
    app.add_entry(description='a Deposit', payee='Joe SixPack', checkno='42A', transfer='Income', increase='212.12')
    # it's important for the test that this txns has no space in its fields
    app.add_entry(description='Withdrawal', payee='Dunno-What-To-Write', checkno='24B', transfer='Cash', decrease='140')
    app.mw.select_transaction_table()
    return app

@with_app(app_two_transactions)
def test_account(app):
    # when using the 'account:' search form, only account are searched. Also, commas can be used
    # to specify more than one term
    app.sfield.query = 'account: withdrawal,inCome'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_amount(app):
    # Amounts can be queried, and the cents, when 0, can be ommited.
    app.sfield.query = '140'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'Withdrawal')

@with_app(app_two_transactions)
def test_query_amount_exact(app):
    # Amount searches are exact.
    app.sfield.query = '212'
    eq_(app.ttable.row_count, 0)
    app.sfield.query = '212.12'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_amount_negative(app):
    # When searching for amount, we ignore the amounts' sign.
    app.sfield.query = '-140'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'Withdrawal')

@with_app(app_two_transactions)
def test_query_description(app):
    # The query is case insensitive and works on description.
    app.sfield.query = 'wiTH'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'Withdrawal')

@with_app(app_two_transactions)
def test_query_checkno(app):
    # The query works on checkno.
    app.sfield.query = '42a'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_checkno_partial(app):
    # We don't match transactions that only partially match checkno (it doesn't make much sense).
    app.sfield.query = '4'
    eq_(app.ttable.row_count, 0)

@with_app(app_two_transactions)
def test_query_from(app):
    # The 'from' account can be queried.
    app.sfield.query = 'desJ'
    eq_(app.ttable.row_count, 2)

@with_app(app_two_transactions)
def test_query_payee(app):
    # The query is case insensitive and works on payee.
    app.sfield.query = 'siX'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_space(app):
    # Querying for a space character doesn't cause a crash. Previously, it did because it was
    # parsed as an amount.
    app.mw.select_transaction_table()
    app.sfield.query = ' ' # no crash
    eq_(app.ttable.row_count, 2) # same as no filter

@with_app(app_two_transactions)
def test_query_to(app):
    # The 'to' account can be queried.
    app.sfield.query = 'Come'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

#--- Three txns with zero amount
def app_three_txns_with_zero_amount():
    app = TestApp()
    app.add_txn(description='foo', amount='212.12')
    app.add_txn(description='bar', amount='140')
    app.add_txn(description='zero-amount', amount='0')
    return app

@with_app(app_three_txns_with_zero_amount)
def test_query_amount_with_zero_amount_txn(app):
    # querying an amount with a zero amount in the stack doesn't cause a crash
    app.sfield.query = '212.12' # no crash
    eq_(app.ttable.row_count, 1)

#--- Split
def app_split():
    app = TestApp()
    splits = [
        ('first', 'memo1', '42', ''),
        ('second', 'Memo2', '', '42'),
        ('third', '', '12', ''),
    ]
    app.add_txn_with_splits(splits)
    return app

@with_app(app_split)    
def test_query_memo(app):
    # memo fields are part of the search query
    app.sfield.query = 'memo2'
    eq_(app.ttable.row_count, 1)

@with_app(app_split) 
def test_query_split_account(app):
    # Any account in a split can match a sfield query.
    app.sfield.query = 'third'
    eq_(app.ttable.row_count, 1)

#--- Three txns filtered
def app_three_txns_filtered():
    app = TestApp()
    app.add_txn(description='foo')
    app.add_txn(description='bar')
    app.add_txn(description='bar')
    app.sfield.query = 'bar'
    app.clear_gui_calls()
    return app

@with_app(app_three_txns_filtered)
def test_change_account(app):
    # Changing selection to another account cancels the filter.
    app.mainwindow.select_balance_sheet()
    eq_(app.sfield.query, '')
    # setting the sfield query didn't make document go to all_transactions again
    eq_(app.mainwindow.current_pane_index, 0)
    app.check_gui_calls(app.sfield_gui, ['refresh'])
    app.mainwindow.select_transaction_table()
    eq_(app.ttable.row_count, 3)

@with_app(app_three_txns_filtered)
def test_change_account_to_bsheet(app):
    # Balance sheet is another notification, so we must also test it in addition to test_change_account.
    app.mainwindow.select_balance_sheet()
    eq_(app.sfield.query, '')
    app.check_gui_calls(app.sfield_gui, ['refresh'])
    app.mainwindow.select_transaction_table()
    eq_(app.ttable.row_count, 3)

@with_app(app_three_txns_filtered)
def test_modify_transaction_out_of_filter(app):
    # When changing a txn so it doesn't match the filter anymore, remove it.
    row = app.ttable.selected_row
    row.description = 'baz'
    app.ttable.save_edits()
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable.selected_indexes, [0])

#--- Grouped and ungrouped txns
def app_grouped_and_ungrouped_txns():
    app = TestApp()
    app.add_group('MyGroup')
    app.add_account('Grouped', group_name='MyGroup')
    app.add_account('Ungrouped')
    app.add_txn(description='first', from_='Grouped')
    app.add_txn(description='second', from_='Ungrouped')
    return app

@with_app(app_grouped_and_ungrouped_txns)
def test_query_group(app):
    app.sfield.query = 'group:foo,mygRoup'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'first')
