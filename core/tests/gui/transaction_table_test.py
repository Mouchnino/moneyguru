# Created By: Virgil Dupras
# Created On: 2008-07-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import csv
from datetime import date
from io import StringIO

from hscommon.testutil import eq_
from hscommon.currency import USD

from ..base import TestApp, with_app, testdata
from ...const import PaneType
from ...gui.transaction_table import TransactionTable
from ...model.date import MonthRange, YearRange
from ...model.account import AccountType

#---
def app_tview_shown():
    app = TestApp()
    app.show_tview()
    return app

@with_app(app_tview_shown)
def test_add_and_cancel(app):
    # Reverting after an add removes the transaction from the list.
    app.ttable.add()
    app.ttable.cancel_edits()
    eq_(app.ttable.row_count, 0)

@with_app(app_tview_shown)
def test_add_change_and_save(app):
    # The add mechanism works as expected.
    app.ttable.add()
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable.selected_indexes, [0])    
    row = app.ttable[0]
    row.description = 'foobar'
    row.from_ = 'some account'
    row.amount = '42'
    app.clear_gui_calls()
    app.ttable.save_edits()
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[0]
    app.istatement.show_selected_account()
    eq_(app.etable_count(), 1)

@with_app(app_tview_shown)
def test_add_twice_then_save(app):
    # Calling add() while in edition calls save_edits().
    # Previously, it wasn't called, causing the row to just stay in the buffer, disapearing at
    # the next refresh
    app.ttable.add()
    app.ttable.add()
    app.ttable.save_edits()
    eq_(app.ttable.row_count, 2)

@with_app(app_tview_shown)
def test_delete_up_to_empty_table_doesnt_cause_crash(app):
    # Don't crash when trying to remove a transaction from an empty list.
    app.ttable.delete()
    assert not app.doc.is_dirty()

@with_app(app_tview_shown)
def test_gui_call_on_filter_applied(app):
    # The ttable's view is refreshed on filter_applied.
    app.mw.select_transaction_table()
    app.clear_gui_calls()
    app.sfield.query = 'foobar'
    app.check_gui_calls(app.ttable_gui, ['refresh'])

@with_app(app_tview_shown)
def test_refresh_on_import(app):
    # When entries are imported, ttable is refreshed
    app.doc.date_range = YearRange(date(2007, 1, 1))
    app.clear_gui_calls()
    app.doc.parse_file_for_import(testdata.filepath('qif', 'checkbook.qif'))
    app.iwin.import_selected_pane()
    assert app.ttable.row_count != 0
    app.check_gui_calls(app.ttable_gui, ['refresh'])

@with_app(app_tview_shown)
def test_show_from_account_when_theres_none_does_nothing(app):
    # show_from_account() when the selected txn has no assigned account does nothing
    app.clear_gui_calls()
    app.ttable.show_from_account() # no crash
    app.check_gui_calls_partial(app.mainwindow_gui, not_expected=['show_entry_table'])

@with_app(app_tview_shown)
def test_strip_account_name_in_from_to_columns(app):
    # String account names in from_to_columns.
    app.add_txn(from_='foo ', to=' bar')
    eq_(app.ttable[0].from_, 'foo')
    eq_(app.ttable[0].to, 'bar')
    # Now, we must make sure that account duplication is correctly detected here.
    app.add_txn(from_='foo ', to=' bar') # reuse accounts
    eq_(app.account_names(), ['foo', 'bar'])

class TestEditionMode:
    def do_setup(self):
        app = TestApp()
        app.mainwindow.select_transaction_table()
        app.ttable.add()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_add_and_save(self, app):
        # Leaving the from/to columns empty don't auto-create an empty named account
        app.ttable.save_edits()
        app.mainwindow.select_income_statement()
        eq_(app.istatement.income.children_count, 2)
    
    @with_app(do_setup)
    def test_change_date_range(self, app):
        # When changing the date range during edition, stop that edition before the date range changes
        app.drsel.select_prev_date_range()
        assert app.ttable.edited is None
    
    @with_app(do_setup)
    def test_delete(self, app):
        # Calling delete() while in edition mode removes the edited transaction and put the table
        # out of edition mode.
        app.ttable.delete()
        eq_(app.ttable.row_count, 0)
        app.ttable.save_edits() # Shouldn't raise anything
    
    @with_app(do_setup)
    def test_duplicate_selected(self, app):
        # When duplicating a transaction, make sure to stop editing so that we don't get an
        # assertion exception later.
        app.ttable.duplicate_selected()
        assert app.ttable.edited is None
    

class TestUnassignedTransactionWithAmount:
    def do_setup(self):
        app = TestApp()
        app.mainwindow.select_transaction_table()
        app.ttable.add()
        app.ttable[0].amount = '42'
        app.ttable.save_edits()
        return app
    
    @with_app(do_setup)
    def test_save_load(self, app):
        # Make sure that unassigned transactions are loaded
        app.do_test_save_load()
    
    @with_app(do_setup)
    def test_show_from_account(self, app):
        # show_from_account() when the selected txn has no assigned account does nothing
        app.ttable.show_from_account() # no crash
        app.check_gui_calls_partial(app.mainwindow_gui, not_expected=['show_entry_table'])
    

#--- One transaction
def app_one_transaction():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('first')
    app.add_txn('11/07/2008', 'description', 'payee', from_='first', to='second', amount='42',
        checkno='24')
    app.clear_gui_calls()
    return app

def assert_row_has_original_attrs(row):
    eq_(row.date, '11/07/2008')
    eq_(row.description, 'description')
    eq_(row.payee, 'payee')
    eq_(row.checkno, '24')
    eq_(row.from_, 'first')
    eq_(row.to, 'second')
    eq_(row.amount, '42.00')
    assert not row.reconciled

@with_app(app_one_transaction)
def test_add_then_delete(app):
    # calling delete() while being in edition mode just cancels the current edit. it does *not*
    # delete the other txn as well.
    app.ttable.add()
    app.ttable.delete()
    eq_(app.ttable.row_count, 1)
    assert app.ttable.edited is None

@with_app(app_one_transaction)
def test_attributes_after_new_txn(app):
    eq_(app.ttable.row_count, 1)
    assert_row_has_original_attrs(app.ttable[0])

@with_app(app_one_transaction)
def test_autofill_amount_format_cache(app):
    # The amount field is correctly autofilled and the cache correctly invalidated
    app.ttable.add()
    app.ttable.edited.amount # cache the format
    app.ttable.edited.description = 'description'
    eq_(app.ttable.edited.amount, '42.00')

@with_app(app_one_transaction)
def test_can_call_can_edit_cell_on_row(app):
    # It's possible to call cen_edit_cell() on the row instance
    assert app.ttable[0].can_edit_cell('date')
    assert not app.ttable[0].can_edit_cell('unknown')

@with_app(app_one_transaction)
def test_cancel_edits(app):
    # cancel_edits() reverts the edited row back to it's old values.
    app.ttable.cancel_edits() # does nothing
    row = app.ttable[0]
    row.date = '12/07/2008'
    app.ttable.cancel_edits()
    # The current implementation keeps the same row instance, but the tests shouldn't require it
    row = app.ttable[0]
    eq_(row.date, '11/07/2008')

@with_app(app_one_transaction)
def test_change_transaction_gui_calls(app):
    # Changing a transaction results in a refresh and a show_selected_row call
    row = app.ttable[0]
    row.date = '12/07/2008'
    app.ttable.save_edits()
    app.check_gui_calls(app.ttable_gui, ['refresh', 'show_selected_row'])

@with_app(app_one_transaction)
def test_duplicate_transaction(app):
    # calling duplicate_selected() duplicates the selected transactions
    app.ttable.duplicate_selected()
    eq_(app.ttable.row_count, 2)
    assert_row_has_original_attrs(app.ttable[0])
    assert_row_has_original_attrs(app.ttable[1])

@with_app(app_one_transaction)
def test_duplicate_transactions(app):
    # duplication works when more than one transaction is selected
    app.mw.duplicate_item()
    app.ttable.select([0, 1])
    app.mw.duplicate_item()
    eq_(app.ttable.row_count, 4)

@with_app(app_one_transaction)
def test_edit_date_out_of_bounds(app):
    # when the date of the edited row is out of the date range, is_date_in_future() or
    # is_date_in_past() return True
    # (range is 07/2008)
    assert not app.ttable[0].is_date_in_past()
    assert not app.ttable[0].is_date_in_future()
    app.ttable[0].date = '01/08/2008'
    assert app.ttable.edited.is_date_in_future()
    assert not app.ttable.edited.is_date_in_past()
    app.ttable[0].date = '30/06/2008'
    assert not app.ttable.edited.is_date_in_future()
    assert app.ttable.edited.is_date_in_past()

@with_app(app_one_transaction)
def test_delete(app):
    # Deleting a transaction updates the graph and makes the 'second' account go away.
    app.ttable.delete()
    eq_(app.ttable.row_count, 0)
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    eq_(list(app.balgraph.data), [])
    eq_(app.account_names(), ['first'])

@with_app(app_one_transaction)
def test_delete_while_filtered(app):
    # Deleting a txn while a filter is applied correctly refreshes the ttable
    app.sfield.query = 'description'
    app.ttable.delete()
    eq_(app.ttable.row_count, 0)

@with_app(app_one_transaction)
def test_edition_mode(app):
    # Initially, no row is edited. setting a row's attr sets the edition mode.
    assert app.ttable.edited is None
    row = app.ttable[0]
    row.date = '12/07/2008'
    assert app.ttable.edited is row
    app.ttable.cancel_edits()
    assert app.ttable.edited is None
    row.date = '12/07/2008'
    app.ttable.save_edits()
    assert app.ttable.edited is None

@with_app(app_one_transaction)
def test_row_is_bold(app):
    # Normal rows are not bold and total rows are bold
    assert not app.ttable[0].is_bold
    assert app.ttable[1].is_bold

@with_app(app_one_transaction)
def test_save_edits(app):
    # save_edits() puts the changes in the buffer down to the model.
    app.ttable.save_edits() # does nothing
    row = app.ttable[0]
    row.date = '12/07/2008'
    row.description = 'foo'
    row.payee = 'bar'
    row.checkno = 'baz'
    row.from_ = 'newfrom'
    row.to = 'newto'
    row.amount = '.42'
    app.ttable.save_edits()
    # This way, we can make sure that what we have in ttable is from the model, not the row buffer
    app.ttable.refresh()
    row = app.ttable[0]
    eq_(row.date, '12/07/2008')
    eq_(row.description, 'foo')
    eq_(row.payee, 'bar')
    eq_(row.checkno, 'baz')
    eq_(row.from_, 'newfrom')
    eq_(row.to, 'newto')
    eq_(row.amount, '0.42')
    # 'newfrom' has been created as an income, and 'newto' as an expense. 'second' has been cleaned
    app.mw.select_income_statement()
    eq_(app.istatement.income.children_count, 3)
    eq_(app.istatement.expenses.children_count, 3)
    eq_(app.istatement.income[0].name, 'newfrom')
    eq_(app.istatement.expenses[0].name, 'newto')
    # now we want to verify that cooking has taken place
    app.istatement.selected = app.istatement.expenses[0]
    app.istatement.show_selected_account()
    row = app.etable[0]
    eq_(row.increase, '0.42')

@with_app(app_one_transaction)
def test_set_date_in_range(app):
    # Setting the date in range doesn't cause useless notifications.
    app.ttable[0].date = '12/07/2008'
    app.clear_gui_calls()
    app.ttable.save_edits()
    app.check_gui_calls(app.drsel_gui, [])

@with_app(app_one_transaction)
def test_set_date_out_of_range(app):
    # Setting the date out of range makes the app's date range change accordingly.
    app.ttable[0].date = '1/08/2008'
    app.clear_gui_calls()
    app.ttable.save_edits()
    eq_(app.doc.date_range, MonthRange(date(2008, 8, 1)))
    expected = ['animate_forward', 'refresh']
    app.check_gui_calls(app.drsel_gui, expected)

@with_app(app_one_transaction)
def test_set_invalid_amount(app):
    # setting an invalid amount reverts to the old amount
    app.ttable[0].amount = 'foo' # no exception
    eq_(app.ttable[0].amount, '42.00')

@with_app(app_one_transaction)
def test_set_row_attr(app):
    # Setting a row's attr puts the table in edition mode, changes the row's buffer, but doesn't
    # touch the transaction.
    row = app.ttable[0]
    row.date = '12/07/2008'
    row.description = 'foo'
    row.payee = 'bar'
    row.checkno = 'baz'
    row.from_ = 'newfrom'
    row.to = 'newto'
    row.amount = '.42'
    eq_(row.date, '12/07/2008')
    eq_(row.description, 'foo')
    eq_(row.payee, 'bar')
    eq_(row.checkno, 'baz')
    eq_(row.from_, 'newfrom')
    eq_(row.to, 'newto')
    eq_(row.amount, '0.42')
    # the changes didn't go down to Transaction
    table = TransactionTable(app.ttable_gui, app.tview)
    table.connect()
    table.show()
    assert_row_has_original_attrs(table[0])

@with_app(app_one_transaction)
def test_show_from_account(app):
    # show_from_account() takes the first account in the From column and shows it in etable.
    app.ttable.show_from_account()
    app.check_current_pane(PaneType.Account, account_name='first')

@with_app(app_one_transaction)
def test_show_to_account(app):
    # show_two_account() takes the first account in the To column and shows it in etable.
    app.ttable.show_to_account()
    app.check_current_pane(PaneType.Account, account_name='second')

@with_app(app_one_transaction)
def test_undo_redo_while_filtered(app):
    # undo/redo while a filter is applied correctly refreshes the ttable
    app.sfield.query = 'description'
    app.ttable.delete()
    app.doc.undo()
    eq_(app.ttable.row_count, 1)
    app.doc.redo()
    eq_(app.ttable.row_count, 0)

@with_app(app_one_transaction)
def test_selection_as_csv(app):
    # selection_as_csv() return a CSV string representing the selection.
    csvdata = app.ttable.selection_as_csv()
    rows = list(csv.reader(StringIO(csvdata), delimiter='\t'))
    # The contents of the columns, in order
    expected = [['11/07/2008', 'description', 'first', 'second', '42.00']]
    eq_(rows, expected)

@with_app(app_one_transaction)
def test_selection_as_csv_different_column_order(app):
    # column order is followed when exporting selection to CSV.
    app.ttable.columns.move_column('date', 3) # after description
    csvdata = app.ttable.selection_as_csv()
    rows = list(csv.reader(StringIO(csvdata), delimiter='\t'))
    expected = [['description', '11/07/2008', 'first', 'second', '42.00']]
    eq_(rows, expected)

class TestTransactionLinkedToNumberedAccounts:
    def do_setup(self):
        app = TestApp()
        app.add_account('account1', account_number='4242')
        app.add_account('account2', account_number='4241')
        # when entering the transactions, accounts are correctly found if their number is found
        app.add_txn(from_='4242 - account1', to='4241', amount='42')
        return app
    
    @with_app(do_setup)
    def test_from_to_column(self, app):
        # When an account is numbered, the from and to column display those numbers with the name.
        eq_(app.ttable[0].from_, '4242 - account1')
        eq_(app.ttable[0].to, '4241 - account2')
    

class TestOneTwoWayTransactionOtherWay:
    def do_setup(self):
        app = TestApp()
        app.add_account('first')
        app.mainwindow.show_account()
        app.add_entry('11/07/2008', transfer='second', increase='42')
        return app
    
    @with_app(do_setup)
    def test_attributes(self, app):
        # The from and to attributes depends on the money flow, not the order of the splits
        app.mainwindow.select_transaction_table()
        row = app.ttable[0]
        eq_(row.from_, 'second')
        eq_(row.to, 'first')
        eq_(row.amount, '42.00')
    

#--- Three-way transaction
def app_three_way_transaction():
    app = TestApp()
    splits = [
        ('first', '', '', '42'),
        ('second', '', '22', ''),
        ('third', '', '20', ''),
    ]
    app.add_txn_with_splits(splits, date='11/07/2008', description='foobar')
    return app

def test_autofill():
    # when the txn a split, don't autofill the from/to fields
    app = app_three_way_transaction()
    app.ttable.add()
    app.ttable.edited.description = 'foobar'
    eq_(app.ttable.edited.from_, '')
    eq_(app.ttable.edited.to, '')

def test_edit_description():
    # save_edits() works for non-two-way splits.
    app = app_three_way_transaction()
    row = app.ttable[0]
    row.description = 'foobar'
    app.ttable.save_edits() # no crash
    eq_(app.ttable[0].description, 'foobar')

def test_edit_from():
    # When edited, the From column is saved.
    app = app_three_way_transaction()
    row = app.ttable[0]
    row.from_ = 'fourth'
    app.ttable.save_edits()
    eq_(app.ttable[0].from_, 'fourth')

#--- Three-way multi-currency transaction
def app_three_way_multi_currency_transaction():
    app = TestApp()
    USD.set_CAD_value(0.8, date(2008, 1, 1))
    app.add_account('first')
    app.mw.show_account()
    app.add_entry('11/07/2008', transfer='second', decrease='42')
    app.tpanel.load()
    app.stable.select([1])
    row = app.stable.selected_row
    row.debit = '20 cad'
    app.stable.save_edits()
    app.stable.add()
    row = app.stable.selected_row
    row.account = 'third'
    row.debit = '22 usd'
    app.stable.save_edits()
    app.tpanel.save()
    app.mainwindow.select_transaction_table()
    return app

#--- Four way txn with unassigned
def app_four_way_txn_with_unassigned():
    app = TestApp()
    splits = [
        ('first', '', '', '22'),
        ('second', '', '22', ''),
        ('', '', '20', ''),
        ('', '', '', '20'),
    ]
    app.add_txn_with_splits(splits, date='11/07/2008')
    return app

@with_app(app_four_way_txn_with_unassigned)
def test_from_and_to_column_show_unassigned_splits(app):
    # The from/to fields show the unassigned splits.
    row = app.ttable[0]
    eq_(row.from_, 'first, Unassigned')
    eq_(row.to, 'second, Unassigned')

class TestTwoWayUnassignedWithAmount:
    def do_setup(self):
        app = TestApp()
        app.mainwindow.select_transaction_table()
        app.ttable.add()
        app.ttable.selected_row.amount = '42'
        app.ttable.save_edits()
        return app
    
    @with_app(do_setup)
    def test_null_unassigned_dont_show_up(self, app):
        # The from/to columns are empty
        # previously, they would show "Unassigned"
        row = app.ttable[0]
        eq_(row.from_, '')
        eq_(row.to, '')
    
        
class TestEmptyTransaction:
    def do_setup(self):
        app = TestApp()
        app.mainwindow.select_transaction_table()
        app.ttable.add()
        app.ttable.save_edits()
        return app
    
    @with_app(do_setup)
    def test_null_unassigned_dont_show_up(self, app):
        # As opposed to null amounts assigned to accounts, null amounts assign to nothing are ignored
        row = app.ttable[0]
        eq_(row.from_, '')
        eq_(row.to, '')
    

class TestTwoWayNullAmounts:
    def do_setup(self):
        app = TestApp()
        app.add_account('first')
        app.mainwindow.show_account()
        app.add_entry('11/07/2008', transfer='second')
        app.mainwindow.select_transaction_table()
        return app
    
    @with_app(do_setup)
    def test_dont_blank_zero(self, app):
        # Null amounts are not blanked
        row = app.ttable[0]
        eq_(row.amount, '0.00')
       
    @with_app(do_setup) 
    def test_from_to(self, app):
        # When the amounts are null, put everything in from and the last in to
        row = app.ttable[0]
        eq_(row.from_, 'first')
        eq_(row.to, 'second')
    

#--- Three way null amounts
def app_three_way_null_amounts():
    app = TestApp()
    splits = [
        ('first', '', '', ''),
        ('second', '', '', ''),
        ('third', '', '', ''),
    ]
    app.add_txn_with_splits(splits, date='11/07/2008')
    return app

@with_app(app_three_way_null_amounts)
def test_can_edit_to(app):
    # The To column can be edited when it represents a single split.
    assert app.ttable.can_edit_cell('to', 0)

@with_app(app_three_way_null_amounts)
def test_edit_to(app):
    # When edited, the To column is saved.
    row = app.ttable[0]
    row.to = 'fourth'
    app.ttable.save_edits()
    eq_(app.ttable[0].to, 'fourth')

@with_app(app_three_way_null_amounts)
def test_from_to(app):
    # When the amounts are null, put everything in from and the last in to.
    row = app.ttable[0]
    eq_(row.from_, 'first, second')
    eq_(row.to, 'third')

class TestTwoTransactionsOneOutOfRange:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account()
        app.mainwindow.show_account()
        app.add_entry('11/06/2008', description='first')
        app.add_entry('11/07/2008', description='second') # The month range has now changed to July 2008
        app.mainwindow.select_transaction_table()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_attributes(self, app):
        # The table only contains transactons in the current date range
        eq_(app.ttable.row_count, 1)
    
    @with_app(do_setup)
    def test_select_prev_date_range(self, app):
        # The transaction table refreshes itself on date range change
        app.drsel.select_prev_date_range()
        row = app.ttable[0]
        eq_(row.description, 'first')
        app.check_gui_calls_partial(app.ttable_gui, ['refresh', 'show_selected_row'])
    
    @with_app(do_setup)
    def test_selection_after_date_range_change(self, app):
        # The selection in the document is correctly updated when the date range changes
        # The tpanel loads the document selection, so this is why we test through it.
        app.drsel.select_prev_date_range()
        app.tpanel.load()
        eq_(app.tpanel.description, 'first')
    

#--- Three transactions
def app_three_transactions():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('11/07/2008', description='first', transfer='first', increase='1')
    app.add_entry('11/07/2008', description='second', transfer='second', increase='2')
    app.add_entry('12/07/2008', description='third', transfer='third', increase='3') 
    app.mw.select_transaction_table()
    return app

@with_app(app_three_transactions)
def test_add_date_and_selection(app):
    # New transactions are added on the same date as the currently selected transaction, after all
    # transactions of the same date.
    app.ttable.select([0])
    app.ttable.add()
    row = app.ttable.edited
    eq_(row.date, '11/07/2008')
    eq_(app.ttable.selected_indexes, [2])

@with_app(app_three_transactions)
def test_delete_last(app):
    # Deleting the last txn makes the selection goes one index before.
    app.ttable.delete()
    eq_(app.ttable.selected_indexes, [1])

@with_app(app_three_transactions)
def test_delete_multiple_selection(app):
    # delete() when having multiple entries selected delete all selected entries.
    app.ttable.select([0, 2])
    app.ttable.delete()
    eq_(app.transaction_descriptions(), ['second'])

@with_app(app_three_transactions)
def test_delete_entries_second(app):
    # Deleting a txn that is not the last does not change the selected index.
    app.ttable.select([1])
    app.ttable.delete()
    eq_(app.ttable.selected_indexes, [1])

@with_app(app_three_transactions)
def test_delete_first(app):
    # Deleting the first entry keeps the selection on the first index
    app.ttable.select([0])
    app.ttable.delete()
    eq_(app.ttable.selected_indexes, [0])

@with_app(app_three_transactions)
def test_delete_second_then_add(app):
    # When deleting the second entry, the 3rd end up selected. if we add a new txn, the txn date
    # must be the date from the 3rd txn
    app.ttable.select([1])
    app.ttable.delete()
    app.ttable.add()
    eq_(app.ttable.edited.date, '12/07/2008')

@with_app(app_three_transactions)
def test_explicit_selection(app):
    # Only the explicit selection is sticky. If the non-explicit selection changes, this doesn't
    # affect the ttable selection.
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[1] # second
    app.istatement.show_selected_account()
    app.mw.select_transaction_table()
    eq_(app.ttable.selected_indexes, [2]) # explicit selection
    # the other way around too
    app.ttable.select([1])
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[2]
    app.istatement.show_selected_account()
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    eq_(app.etable.selected_indexes, [1]) # explicit selection

@with_app(app_three_transactions)
def test_selection(app):
    # TransactionTable stays in sync with EntryTable.
    app.ttable.hide() # this disconnect scheme will eventually be embedded in the main testcase
    app.etable.select([0, 1])
    app.clear_gui_calls()
    app.etable.hide()
    app.ttable.show()
    eq_(app.ttable.selected_indexes, [0, 1])
    app.check_gui_calls(app.ttable_gui, ['show_selected_row'])

@with_app(app_three_transactions)
def test_selection_changed_when_filtering_out(app):
    # selected transactions becoming filtered out are not selected anymore. Also, the selection
    # is updated at the document level
    app.ttable.select([0]) # first
    app.sfield.query = 'second'
    eq_(app.ttable.selected_row.description, 'second')
    app.mw.edit_item()
    eq_(app.tpanel.description, 'second')

@with_app(app_three_transactions)
def test_total_row(app):
    # The total row shows total amount with the date being the last day of the date range.
    row = app.ttable[3]
    eq_(row.date, '31/12/2008')
    eq_(row.description, 'TOTAL')
    eq_(row.amount, '6.00')

class TestThreeTransactionsEverythingReconciled:
    def do_setup(self):
        app = TestApp()
        app.add_account('first')
        app.add_account('second')
        app.mainwindow.select_balance_sheet()
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.show_selected_account()
        app.add_entry('19/07/2008', description='entry 1', increase='1')
        app.add_entry('20/07/2008', description='entry 2', transfer='second', increase='2')
        app.add_entry('20/07/2008', description='entry 3', increase='3')
        app.aview.toggle_reconciliation_mode()
        app.etable[0].toggle_reconciled()
        app.etable[1].toggle_reconciled()
        app.etable[2].toggle_reconciled()
        app.mainwindow.select_balance_sheet()
        app.bsheet.selected = app.bsheet.assets[1]
        app.bsheet.show_selected_account()
        app.etable[0].toggle_reconciled() # we also reconcile the other side of the 2nd entry
        app.aview.toggle_reconciliation_mode() # commit reconciliation
        app.mainwindow.select_transaction_table()
        return app
    
    @with_app(do_setup)
    def test_move_while_filtered(self, app):
        # The ttable is correctly updated after a move with a filter applied
        app.sfield.query = 'entry'
        app.ttable.move([1], 3)
        eq_(app.ttable[1].description, 'entry 3')
        eq_(app.ttable[2].description, 'entry 2')
    
    @with_app(do_setup)
    def test_row_reconciled(self, app):
        assert app.ttable[0].reconciled
    

#--- Transaction created through the ttable
def app_transaction_created_through_ttable():
    app = TestApp()
    app.mw.select_transaction_table()
    app.ttable.add()
    row = app.ttable.edited
    row.description = 'foo'
    row.payee = 'bar'
    row.from_ = 'first'
    row.to = 'second'
    row.amount = '42'
    app.ttable.save_edits()
    return app

@with_app(app_transaction_created_through_ttable)
def test_completion(app):
    # Here, we want to make sure that complete() works, but we also want to make sure it is 
    # unaffected by entries (which means selected account and stuff).
    # There is *no* selected account
    ce = app.completable_edit('description')
    ce.text = 'f'
    eq_(ce.completion, 'oo')
    ce.attrname = 'payee'
    ce.text = 'b'
    eq_(ce.completion, 'ar')
    ce.attrname = 'from'
    ce.text = 'f'
    eq_(ce.completion, 'irst')
    ce.text = 's'
    eq_(ce.completion, 'econd')
    ce.attrname = 'to'
    ce.text = 'f'
    eq_(ce.completion, 'irst')
    ce.text = 's'
    eq_(ce.completion, 'econd')

#--- Transaction on last day of range
def app_txn_on_last_day_of_range(monkeypatch):
    app = TestApp()
    monkeypatch.patch_today(2010, 3, 21)
    app.add_txn('31/12/2010')
    return app

@with_app(app_txn_on_last_day_of_range)
def test_added_txn_is_correctly_selected(app):
    # Previously, the total row would mess things up if a transaction was added while a selection
    # with the same date as the total row was active. A row would be added at the correct place, but
    # the *total row* would end up selected and edited.
    app.ttable.add()
    eq_(len(app.ttable.rows), 2)
    eq_(app.ttable.selected_index, 1)

#--- Load file
def app_load_file():
    app = TestApp()
    app.doc.date_range = MonthRange(date(2008, 2, 1))
    app.doc.load_from_xml(testdata.filepath('moneyguru', 'simple.moneyguru'))
    app.mainwindow.select_transaction_table()
    return app

@with_app(app_load_file)
def test_added_txn_has_selected_txn_date(app):
    # The newly added txn will have the last transactions' date rather then today's date
    app.ttable.add()
    eq_(app.ttable.edited.date, '19/02/2008')

@with_app(app_load_file)
def test_table_is_refreshed_upon_load(app):
    # The transaction table refreshes upon FILE_LOADED.
    eq_(app.ttable.row_count, 4)
    eq_(app.ttable.selected_indexes, [3])

#--- Autofill
def app_autofill():
    app = TestApp()
    app.add_account('Checking')
    app.mw.show_account()
    app.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42')
    return app

@with_app(app_autofill)
def test_autofill_after_column_change(app):
    # When setting the Table's columns, only the visible columns to the right of the edited one are
    # auto-filled.
    app.vopts.transaction_table_payee = False
    app.ttable.columns.move_column('from', 0)
    app.ttable.add()
    row = app.ttable.edited
    row.description = 'Deposit'
    eq_(row.amount, '42.00')
    eq_(row.payee, '')
    eq_(row.from_, '')
    eq_(row.to, 'Checking')

@with_app(app_autofill)
def test_autofill_doesnt_overwrite_nonblank_fields(app):
    # Autofill doesn't touch fields that have a non-blank value.
    app.ttable.add()
    row = app.ttable.edited
    row.payee = 'foo'
    row.from_ = 'bar'
    row.to = 'baz'
    row.amount = '12'
    row.description = 'Deposit'
    eq_(row.amount, '12.00')
    eq_(row.payee, 'foo')
    eq_(row.from_, 'bar')
    eq_(row.to, 'baz')
    app.ttable.cancel_edits()
    # Now we need another row to try for description
    app.ttable.add()
    row = app.ttable.edited
    row.description = 'foo'
    row.payee = 'Payee'
    eq_(row.description, 'foo')

@with_app(app_autofill)
def test_autofill_is_case_sensitive(app):
    # When the case of a description/transfer value does not match an entry, completion do not occur.
    app.ttable.add()
    row = app.ttable.edited
    row.description = 'deposit'
    row.from_ = 'deposit'
    row.to = 'deposit'
    eq_(row.amount, '0.00')

@with_app(app_autofill)
def test_autofill_ignores_blank(app):
    # Blank values never result in autofill.
    app.mw.select_transaction_table()
    row = app.ttable[0]
    row.description = ''
    app.ttable.save_edits()
    app.ttable.add()
    row = app.ttable.edited
    row.description = ''
    eq_(row.payee, '')

@with_app(app_autofill)
def test_autofill_on_set_from(app):
    # Setting 'from' autocompletes the rest.
    app.vopts.transaction_table_payee = True
    app.ttable.columns.move_column('from', 0)
    app.ttable.add()
    row = app.ttable.edited
    row.from_ = 'Salary'
    eq_(row.amount, '42.00')
    eq_(row.description, 'Deposit')
    eq_(row.payee, 'Payee')
    eq_(row.to, 'Checking')

@with_app(app_autofill)
def test_autofill_on_set_to(app):
    # Setting 'to' autocompletes the rest.
    app.vopts.transaction_table_payee = True
    app.ttable.columns.move_column('to', 0)
    app.ttable.add()
    row = app.ttable.edited
    row.to = 'Checking'
    eq_(row.amount, '42.00')
    eq_(row.description, 'Deposit')
    eq_(row.payee, 'Payee')
    eq_(row.from_, 'Salary')

@with_app(app_autofill)
def test_autofill_on_set_description(app):
    # Setting a description autocompletes the amount and the transfer.
    app.vopts.transaction_table_payee = True
    app.ttable.add()
    row = app.ttable.edited
    row.description = 'Deposit'
    eq_(row.amount, '42.00')
    eq_(row.payee, 'Payee')
    eq_(row.from_, 'Salary')
    eq_(row.to, 'Checking')

@with_app(app_autofill)
def test_autofill_on_set_payee(app):
    # Setting a transfer autocompletes the amount and the description.
    app.vopts.transaction_table_payee = True
    app.ttable.columns.move_column('payee', 0)
    app.ttable.add()
    row = app.ttable.edited
    row.payee = 'Payee'
    eq_(row.amount, '42.00')
    eq_(row.description, 'Deposit')
    eq_(row.from_, 'Salary')
    eq_(row.to, 'Checking')

@with_app(app_autofill)
def test_autofill_only_when_the_value_changes(app):
    # When editing an existing entry, don't autofill if the value set hasn't changed
    app.ttable.add()
    row = app.ttable.edited
    row.description = 'Deposit' # everything is autofilled
    row.payee = ''
    row.description = 'Deposit'
    eq_(row.payee, '')

@with_app(app_autofill)
def test_autofill_uses_the_latest_entered(app):
    # Even if the date is earlier, we use this newly added entry because it's the latest modified.
    app.add_entry('9/10/2007', 'Deposit', increase='12.34')
    app.ttable.add()
    row = app.ttable.edited
    row.description = 'Deposit'
    eq_(row.amount, '12.34')

class TestSevenEntries:
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.mainwindow.show_account()
        app.doc.date_range = MonthRange(date(2008, 1, 1))
        app.add_entry('1/1/2008', description='txn 1')
        app.add_entry('2/1/2008', description='txn 2')
        app.add_entry('2/1/2008', description='txn 3')
        app.add_entry('2/1/2008', description='txn 4')
        app.add_entry('2/1/2008', description='txn 5')
        app.add_entry('3/1/2008', description='txn 6')
        app.add_entry('3/1/2008', description='txn 7')
        return app
    
    @with_app(do_setup)
    def test_can_reorder_entry(self, app):
        # Move is allowed only when it makes sense
        app.mainwindow.select_transaction_table()
        assert not app.ttable.can_move([0], 2) # Not the same date
        assert not app.ttable.can_move([2], 0) # Likewise
        assert not app.ttable.can_move([1], 1) # Moving to the same row doesn't change anything
        assert not app.ttable.can_move([1], 2) # Moving to the next row doesn't change anything
        assert app.ttable.can_move([1], 3)
        assert app.ttable.can_move([1], 4)  # Can move to the end of the day
        assert not app.ttable.can_move([3], 4) # Moving to the next row doesn't change anything
        assert app.ttable.can_move([5], 7)  # Can move beyond the bounds of the entry list
        assert not app.ttable.can_move([6], 7) # Moving to the next row doesn't change anything
        assert not app.ttable.can_move([6], 8) # Out of range destination by 2 doesn't cause a crash
    
    @with_app(do_setup)
    def test_can_reorder_entry_multiple(self, app):
        # Move is allowed only when it makes sense
        app.mainwindow.select_transaction_table()
        assert app.ttable.can_move([1, 2], 4) # This one is valid
        assert not app.ttable.can_move([1, 0], 4) # from_indexes are on different days
        assert not app.ttable.can_move([1, 2], 3) # Nothing moving (just next to the second index)
        assert not app.ttable.can_move([1, 2], 1) # Nothing moving (in the middle of from_indexes)
        assert not app.ttable.can_move([1, 2], 2) # same as above
        assert not app.ttable.can_move([2, 1], 2) # same as above, but making sure order doesn't matter
        assert app.ttable.can_move([1, 3], 3) # Puts 2 between 3 and 4
        assert app.ttable.can_move([1, 3], 1) # Puts 4 between 2 and 3
        assert app.ttable.can_move([1, 3], 2) # same as above
    
    @with_app(do_setup)
    def test_change_date(self, app):
        # When chaing a txn date, the txn goes at the last position of its new date
        app.mainwindow.select_transaction_table()
        app.ttable.select([2]) # txn 3
        row = app.ttable[2]
        row.date = '3/1/2008'
        app.ttable.save_edits()
        eq_(app.ttable[6].description, 'txn 3')
        eq_(app.ttable.selected_indexes, [6])
    
    @with_app(do_setup)
    def test_move_entry_to_the_end_of_the_day(self, app):
        # Moving a txn to the end of the day works
        app.mainwindow.select_transaction_table()
        app.ttable.move([1], 5)
        eq_(app.transaction_descriptions()[:5], ['txn 1', 'txn 3', 'txn 4', 'txn 5', 'txn 2'])
    
    @with_app(do_setup)
    def test_move_entry_to_the_end_of_the_list(self, app):
        # Moving a txn to the end of the list works
        app.mainwindow.select_transaction_table()
        app.ttable.move([5], 7)
        eq_(app.transaction_descriptions()[5:], ['txn 7', 'txn 6'])
    
    @with_app(do_setup)
    def test_reorder_entry(self, app):
        # Moving a txn reorders the entries.
        app.mainwindow.select_transaction_table()
        app.ttable.move([1], 3)
        eq_(app.transaction_descriptions()[:4], ['txn 1', 'txn 3', 'txn 2', 'txn 4'])
    
    @with_app(do_setup)
    def test_reorder_entry_multiple(self, app):
        # Multiple txns can be re-ordered at once
        app.mainwindow.select_transaction_table()
        app.ttable.move([1, 2], 4)
        eq_(app.transaction_descriptions()[:4], ['txn 1', 'txn 4', 'txn 2', 'txn 3'])
    
    @with_app(do_setup)
    def test_reorder_entry_makes_the_app_dirty(self, app):
        # reordering txns makes the app dirty
        app.save_file()
        app.mainwindow.select_transaction_table()
        app.ttable.move([1], 3)
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_selection_follows(self, app):
        # The selection follows when we move the selected txn.
        app.mainwindow.select_transaction_table()
        app.ttable.select([1])
        app.ttable.move([1], 3)
        eq_(app.ttable.selected_indexes, [2])
        app.ttable.move([2], 1)
        eq_(app.ttable.selected_indexes, [1])
    
    @with_app(do_setup)
    def test_selection_follows_multiple(self, app):
        # The selection follows when we move the selected txns
        app.mainwindow.select_transaction_table()
        app.ttable.select([1, 2])
        app.ttable.move([1, 2], 4)
        eq_(app.ttable.selected_indexes, [2, 3])
    
    @with_app(do_setup)
    def test_selection_stays(self, app):
        # The selection stays on the same txn if we don't move the selected one
        app.mainwindow.select_transaction_table()
        app.ttable.select([2])
        app.ttable.move([1], 3)
        eq_(app.ttable.selected_indexes, [1])
        app.ttable.move([2], 1)
        eq_(app.ttable.selected_indexes, [2])
        app.ttable.select([4])
        app.ttable.move([1], 3)
        eq_(app.ttable.selected_indexes, [4])
    

class TestFourEntriesOnTheSameDate:
    # Four entries in the same account on the same date
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.mainwindow.show_account()
        app.doc.date_range = MonthRange(date(2008, 1, 1))
        app.add_entry('1/1/2008', description='txn 1')
        app.add_entry('1/1/2008', description='txn 2')
        app.add_entry('1/1/2008', description='txn 3')
        app.add_entry('1/1/2008', description='txn 4')
        app.mainwindow.select_transaction_table()
        return app
    
    @with_app(do_setup)
    def test_can_reorder_multiple(self, app):
        # It's not possible to move entries in the middle of a gapless multiple selection
        assert not app.ttable.can_move([0, 1, 2, 3], 2) # Nothing moving (in the middle of from_indexes)
    
    @with_app(do_setup)
    def test_move_entries_up(self, app):
        # Moving more than one entry up does nothing
        app.ttable.select([1, 2])
        app.ttable.move_up()
        eq_(app.transaction_descriptions(), ['txn 1', 'txn 2', 'txn 3', 'txn 4'])
    
    @with_app(do_setup)
    def test_move_entry_down(self, app):
        # Move an entry down a couple of times
        app.ttable.select([2])
        app.ttable.move_down()
        eq_(app.transaction_descriptions(), ['txn 1', 'txn 2', 'txn 4', 'txn 3'])
        app.ttable.move_down()
        eq_(app.transaction_descriptions(), ['txn 1', 'txn 2', 'txn 4', 'txn 3'])
    
    @with_app(do_setup)
    def test_move_entry_up(self, app):
        # Move an entry up a couple of times
        app.ttable.select([1])
        app.ttable.move_up()
        eq_(app.transaction_descriptions(), ['txn 2', 'txn 1', 'txn 3', 'txn 4'])
        app.ttable.move_up()
        eq_(app.transaction_descriptions(), ['txn 2', 'txn 1', 'txn 3', 'txn 4'])
    

class TestWithBudget:
    def do_setup(self, monkeypatch):
        app = TestApp()
        monkeypatch.patch_today(2008, 1, 27)
        app.drsel.select_today_date_range()
        app.add_account('Some Expense', account_type=AccountType.Expense)
        app.add_budget('Some Expense', None, '100')
        app.mw.select_transaction_table()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_budget_spawns(self, app):
        # When a budget is set budget transaction spawns show up in ttable, at the end of each month.
        eq_(app.ttable.row_count, 12)
        eq_(app.ttable[0].amount, '100.00')
        eq_(app.ttable[0].date, '31/01/2008')
        eq_(app.ttable[0].to, 'Some Expense')
        assert app.ttable[0].is_budget
        eq_(app.ttable[11].date, '31/12/2008')
        # Budget spawns can't be edited
        assert not app.ttable.can_edit_cell('date', 0)
        app.mw.edit_item() # budget spawns can't be edited
        app.tpanel_gui.check_gui_calls_partial(not_expected=['post_load'])
    

#--- Generators
def test_attributes():
    def check(app, index, expected):
        row = app.ttable[index]
        for attrname, value in expected.items():
            eq_(getattr(row, attrname), value)
    
    # Transactions with more than 2 splits are supported.
    app = app_three_way_transaction()
    yield check, app, 0, {'from_': 'first', 'to': 'second, third', 'amount': '42.00'}
    
    # When the 'to' side has more than one currency, convert everything to the account's currency.
    app = app_three_way_multi_currency_transaction()
    # (42 + 22 + (20 / .8)) / 2
    yield check, app, 0, {'amount': '44.50'}

def test_can_edit():
    def check(app, index, uneditable_fields):
        for colname in ['date', 'description', 'payee', 'checkno', 'from', 'to', 'amount']:
            if colname in uneditable_fields:
                assert not app.ttable.can_edit_cell(colname, index)
            else:
                assert app.ttable.can_edit_cell(colname, index)                
        assert not app.ttable.can_edit_cell('unknown', index)
    
    # All fields are editable except "to" which contains 2 accounts (from has only one so it's
    # editable) and "amount" because there's more than one split.
    app = app_three_way_transaction()
    yield check, app, 0, ('to', 'amount')
    
    # When the transaction is multi-currency, the amount can't be edited.
    app = app_three_way_multi_currency_transaction()
    yield check, app, 0, ('to', 'amount')
    
    # All columns can be edited, except unknown ones
    app = app_one_transaction()
    yield check, app, 0, []
