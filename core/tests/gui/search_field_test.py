# Created By: Virgil Dupras
# Created On: 2008-07-21
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ...const import PaneType
from ..base import TestApp, with_app

#--- Pristine
@with_app(TestApp)    
def test_set_query(app):
    # Setting the 'query' property works"""
    app.sfield.text = 'foobar'
    eq_(app.sfield.text, 'foobar')

@with_app(TestApp)    
def test_set_query_selects_transaction_pane(app):
    # Setting the search query selects the transaction tab specifically. Previously, the tab that
    # was selected was always the 3rd one, regardless of the type.
    app.mw.close_pane(2) # we close the transactions pane
    app.sfield.text = 'foo'
    app.check_current_pane(PaneType.Transaction)

#--- Two transactions
def app_two_transactions():
    app = TestApp()
    app.add_account('Desjardins')
    app.mw.show_account()
    app.add_entry(description='a Deposit', payee='Joe SixPack', checkno='42A', transfer='Income', increase='212.12')
    # it's important for the test that this txns has no space in its fields
    app.add_entry(description='Withdrawal', payee='Dunno-What-To-Write', checkno='24B', transfer='Cash', decrease='140')
    app.show_tview()
    return app

@with_app(app_two_transactions)
def test_account(app):
    # when using the 'account:' search form, only account are searched. Also, commas can be used
    # to specify more than one term
    app.sfield.text = 'account: withdrawal,inCome'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_amount(app):
    # Amounts can be queried, and the cents, when 0, can be ommited.
    app.sfield.text = '140'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'Withdrawal')

@with_app(app_two_transactions)
def test_query_amount_exact(app):
    # Amount searches are exact.
    app.sfield.text = '212'
    eq_(app.ttable.row_count, 0)
    app.sfield.text = '212.12'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_amount_negative(app):
    # When searching for amount, we ignore the amounts' sign.
    app.sfield.text = '-140'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'Withdrawal')

@with_app(app_two_transactions)
def test_query_description(app):
    # The query is case insensitive and works on description.
    app.sfield.text = 'wiTH'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'Withdrawal')

@with_app(app_two_transactions)
def test_query_checkno(app):
    # The query works on checkno.
    app.sfield.text = '42a'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_checkno_partial(app):
    # We don't match transactions that only partially match checkno (it doesn't make much sense).
    app.sfield.text = '4'
    eq_(app.ttable.row_count, 0)

@with_app(app_two_transactions)
def test_query_from(app):
    # The 'from' account can be queried.
    app.sfield.text = 'desJardins'
    eq_(app.ttable.row_count, 2)

@with_app(app_two_transactions)
def test_query_payee(app):
    # The query is case insensitive and works on payee.
    app.sfield.text = 'siX'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_query_space(app):
    # Querying for a space character doesn't cause a crash. Previously, it did because it was
    # parsed as an amount.
    app.show_tview()
    app.sfield.text = ' ' # no crash
    eq_(app.ttable.row_count, 2) # same as no filter

@with_app(app_two_transactions)
def test_query_to(app):
    # The 'to' account can be queried.
    app.sfield.text = 'inCome'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'a Deposit')

@with_app(app_two_transactions)
def test_dont_parse_amount_with_expression(app):
    # Don't parse the amount with the 'with_expression' option. It doesn't make sense.
    app.sfield.text = '100+40' # The txn with the '140' amount shouldn't show up.
    eq_(app.ttable.row_count, 0)

#---
def app_ambiguity_in_txn_values():
    # Transactions have similar values in different fields
    app = TestApp()
    app.add_txn(description='foo1', payee='foo2', checkno='foo3', from_='foo4', to='foo5', amount='42')
    app.add_txn(description='foo2', payee='foo3', checkno='foo4', from_='foo5', to='foo1', amount='43')
    return app

@with_app(app_ambiguity_in_txn_values)
def test_targeted_description_search(app):
    app.sfield.text = 'description:foo1'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'foo1')

@with_app(app_ambiguity_in_txn_values)
def test_targeted_payee_search(app):
    app.sfield.text = 'payee:foo2'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'foo1')

@with_app(app_ambiguity_in_txn_values)
def test_targeted_checkno_search(app):
    app.sfield.text = 'checkno:foo3'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'foo1')

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
    app.sfield.text = '212.12' # no crash
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
    app.sfield.text = 'memo2'
    eq_(app.ttable.row_count, 1)

@with_app(app_split) 
def test_query_split_account(app):
    # Any account in a split can match a sfield query.
    app.sfield.text = 'third'
    eq_(app.ttable.row_count, 1)

#--- Three txns filtered
def app_three_txns_filtered():
    app = TestApp()
    app.add_txn(description='foo')
    app.add_txn(description='bar')
    app.add_txn(description='bar')
    app.sfield.text = 'bar'
    app.clear_gui_calls()
    return app

@with_app(app_three_txns_filtered)
def test_change_account(app):
    # Changing selection to another account cancels the filter.
    app.show_nwview()
    eq_(app.sfield.text, '')
    # setting the sfield query didn't make document go to all_transactions again
    eq_(app.mainwindow.current_pane_index, 0)
    app.sfield.view.check_gui_calls(['refresh'])
    app.show_tview()
    eq_(app.ttable.row_count, 3)

@with_app(app_three_txns_filtered)
def test_change_account_to_bsheet(app):
    # Balance sheet is another notification, so we must also test it in addition to test_change_account.
    app.show_nwview()
    eq_(app.sfield.text, '')
    app.sfield.view.check_gui_calls(['refresh'])
    app.show_tview()
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
    app.sfield.text = 'group:foo,mygRoup'
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].description, 'first')
