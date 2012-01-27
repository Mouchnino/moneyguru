# Created By: Virgil Dupras
# Created On: 2008-08-02
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...document import FilterType
from ...model.account import AccountType

class TestPristine:
    @with_app(TestApp)
    def test_attributes(self, app):
        # the filter bars start out as unfiltered, and both etable and ttable have one.
        app.show_tview()
        assert app.tfbar.filter_type is None
        app.add_account('foo')
        app.show_account('foo')
        assert app.efbar.filter_type is None
    

class TestTransactionsOfEachType:
    def do_setup(self):
        app = TestApp()
        app.add_account('asset 1')
        app.add_account('asset 2')
        app.show_account()
        app.add_entry(description='first', transfer='Income', increase='1')
        app.add_entry(description='second', increase='2')
        app.add_entry(description='third', transfer='Expense', decrease='3')
        app.add_entry(description='fourth', transfer='asset 1', decrease='4')
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_efbar_filter_expenses(self, app):
        #The etable's expense filter makes it only show entries with a decrease
        app.efbar.filter_type = FilterType.Expense # decrease
        app.check_gui_calls(app.etable_gui, ['refresh'])
        eq_(app.etable_count(), 2)
        eq_(app.etable[0].description, 'third')
        eq_(app.etable[1].description, 'fourth')
        #The ttable's expense filter makes it only show entries with a transfer to an expense.
        app.show_tview()
        app.tfbar.view.check_gui_calls(['refresh']) # refreshes on connect()
        assert app.tfbar.filter_type is FilterType.Expense
        eq_(app.ttable.row_count, 1)
        eq_(app.ttable[0].description, 'third')
    
    @with_app(do_setup)
    def test_efbar_filter_income(self, app):
        #The etable's income filter makes it only show entries with an increase.
        app.efbar.filter_type = FilterType.Income
        app.check_gui_calls(app.etable_gui, ['refresh'])
        eq_(app.etable_count(), 2)
        eq_(app.etable[0].description, 'first')
        eq_(app.etable[1].description, 'second')
        #The etable's income filter makes it only show entries with a transfer to an income.
        app.show_tview()
        app.tfbar.view.check_gui_calls(['refresh']) # refreshes on connect()
        assert app.tfbar.filter_type is FilterType.Income
        eq_(app.ttable.row_count, 1)
        eq_(app.ttable[0].description, 'first')
    
    @with_app(do_setup)
    def test_efbar_filter_transfer(self, app):
        #The etable's transfer filter makes it only show entries with a transfer to an asset/liability.
        app.efbar.filter_type = FilterType.Transfer
        app.check_gui_calls(app.etable_gui, ['refresh'])
        eq_(app.etable_count(), 1)
        eq_(app.etable[0].description, 'fourth')
        app.show_tview()
        app.tfbar.view.check_gui_calls(['refresh']) # refreshes on connect()
        assert app.tfbar.filter_type is FilterType.Transfer
        eq_(app.ttable.row_count, 1)
        eq_(app.ttable[0].description, 'fourth')
    
    @with_app(do_setup)
    def test_efbar_filter_unassigned(self, app):
        # The etable's unassigned filter makes it only show unassigned entries. going to ttable keeps
        # the filter on.
        app.efbar.filter_type = FilterType.Unassigned
        app.check_gui_calls(app.etable_gui, ['refresh'])
        eq_(app.etable_count(), 1)
        eq_(app.etable[0].description, 'second')
        app.show_tview()
        app.tfbar.view.check_gui_calls(['refresh']) # refreshes on connect()
        assert app.tfbar.filter_type is FilterType.Unassigned
        eq_(app.ttable.row_count, 1)
    
    @with_app(do_setup)
    def test_enable_disable_buttons(self, app):
        # The enable disable mechanism of the income, expense and transfer buttons work as expected
        app.efbar.filter_type = FilterType.Transfer
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.clear_gui_calls()
        app.show_account()
        assert app.efbar.filter_type is None
        app.efbar.view.check_gui_calls(['refresh', 'disable_transfers'])
        app.show_tview()
        app.tfbar.view.check_gui_calls(['refresh']) # no disable
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        app.efbar.view.check_gui_calls(['refresh', 'enable_transfers'])
    
    @with_app(do_setup)
    def test_enable_disable_buttons_through_etable_cycling(self, app):
        # filter bar's enable/disable actions are correctly triggered when cycling through transfer
        # accounts in etable. Previously, selected_account would be used instead of shown_account.
        app.etable.select([0]) # entry with transfer to income
        app.etable.show_transfer_account() # showing Income
        app.link_aview()
        app.efbar.view.check_gui_calls(['refresh', 'disable_transfers'])
        app.etable.show_transfer_account() # showing asset 2
        app.link_aview()
        # We only enable/disable transfers on creation, not on every refresh
        app.efbar.view.check_gui_calls(['refresh'])
    
    @with_app(do_setup)
    def test_multiple_filters_at_the_same_time(self, app):
        # Having an unassigned filter at the same time as a search filter works as expected.
        app.show_tview()
        app.tfbar.filter_type = FilterType.Unassigned
        app.sfield.text = 'first'
        eq_(app.ttable.row_count, 0)
    
    @with_app(do_setup)
    def test_allow_change_in_fbar_when_in_income_account(self, app):
        # There was a bug (#297) where the fbar, when in an income/expense account, would always
        # reset the filter to None on refresh, making it impossible to apply any filter.
        app.show_account('Income')
        app.efbar.filter_type = FilterType.Income
        eq_(app.efbar.filter_type, FilterType.Income)
    

class TestThreeEntriesOneReconciled:
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.add_entry('1/1/2008', 'one')
        app.add_entry('20/1/2008', 'two')
        app.add_entry('31/1/2008', 'three')
        app.aview.toggle_reconciliation_mode()
        app.etable.select([1])
        row = app.etable.selected_row
        row.toggle_reconciled()
        app.aview.toggle_reconciliation_mode() # commit reonciliation
        return app
    
    @with_app(do_setup)
    def test_efbar_not_reconciled(self, app):
        app.efbar.filter_type = FilterType.NotReconciled
        eq_(app.etable_count(), 2)
        eq_(app.etable[0].description, 'one')
        app.show_tview()
        eq_(app.ttable.row_count, 2)
        eq_(app.ttable[1].description, 'three')
    
    @with_app(do_setup)
    def test_efbar_reconciled(self, app):
        app.efbar.filter_type = FilterType.Reconciled
        eq_(app.etable_count(), 1)
        eq_(app.etable[0].description, 'two')
        app.show_tview()
        eq_(app.ttable.row_count, 1)
        eq_(app.ttable[0].description, 'two')
    

#--- Expense split between asset and liability
# A transaction going to an expense, half coming from an asset, the other half coming from a
# liability.
def app_expense_split_between_asset_and_liability():
    app = TestApp()
    app.add_account('liability', account_type=AccountType.Liability)
    app.add_account('asset')
    app.show_account()
    app.add_entry(transfer='expense', decrease='100')
    app.tpanel.load()
    app.stable.add()
    app.stable[2].account = 'liability'
    app.stable[2].credit = '50'
    app.stable.save_edits()
    app.tpanel.save()
    app.clear_gui_calls()
    # we're now on etable, looking at 'asset'
    return app
    
def test_efbar_increase_decrease():
    app = app_expense_split_between_asset_and_liability()
    app.efbar.filter_type = FilterType.Income # increase
    eq_(app.etable_count(), 0)
    app.efbar.filter_type = FilterType.Expense # decrease
    eq_(app.etable_count(), 1)
    # now, let's go to the liability side
    app.show_nwview()
    app.bsheet.selected = app.bsheet.liabilities[0]
    app.show_account()
    # we're still on FilterType.Expense (decrease)
    eq_(app.etable_count(), 0)
    app.efbar.filter_type = FilterType.Income # increase
    eq_(app.etable_count(), 1)
