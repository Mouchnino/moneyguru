# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from nose.tools import eq_

from ...model.account import EXPENSE
from ..base import TestCase

class TransactionsWithInfoFilledUp(TestCase):
    # Transactions with all kinds of info filled up (desc, payee, checkno...)
    def setUp(self):
        self.create_instances()
        self.add_txn(date='30/11/2009', description='desc', payee='payee', checkno='123',
            from_='from', to='to', amount='42')
        self.add_txn(date='01/12/2009', description='aaa', payee='zzz', checkno='321',
            from_='aaa', to='zzz', amount='41')
        self.add_txn(date='02/12/2009', description='zzz', payee='aaa', checkno='000',
            from_='zzz', to='aaa', amount='43')
    
    def test_sort_by_date(self):
        # Sorting by date use the datetime value for sorting, not the string value.
        self.ttable.sort_by('date')
        eq_(self.ttable[0].date, '30/11/2009')
        eq_(self.ttable[1].date, '01/12/2009')
        eq_(self.ttable[2].date, '02/12/2009')
    
    def test_sort_by_description(self):
        # Sorting by description works
        self.ttable.sort_by('description')
        eq_(self.ttable[0].description, 'aaa')
        eq_(self.ttable[1].description, 'desc')
        eq_(self.ttable[2].description, 'zzz')
    
    def test_sort_by_description_desc(self):
        # When `desc` is True, the sort order is inverted
        self.ttable.sort_by('description', desc=True)
        eq_(self.ttable[0].description, 'zzz')
        eq_(self.ttable[1].description, 'desc')
        eq_(self.ttable[2].description, 'aaa')
    
    def test_sort_by_from(self):
        # we deal with the from --> from_ escaping. At the time this test was written, it didn't
        # fail because the we're just fetching '_from', but it's still a case that can very likely
        # fail in future re-factorings.
        self.ttable.sort_by('from')
        eq_(self.ttable[0].from_, 'aaa')
        eq_(self.ttable[1].from_, 'from')
        eq_(self.ttable[2].from_, 'zzz')
    

class TransactionsWithAccents(TestCase):
    # Transactions with accented letters in their descriptions
    def setUp(self):
        self.create_instances()
        self.add_txn(description='aaa')
        self.add_txn(description='ZZZ')
        self.add_txn(description='ez')
        self.add_txn(description='éa')
    
    def test_sort_by_description(self):
        # Letters with accents are treated as if they didn't have their accent.
        self.ttable.sort_by('description')
        eq_(self.ttable[0].description, 'aaa')
        eq_(self.ttable[1].description, 'éa')
        eq_(self.ttable[2].description, 'ez')
        eq_(self.ttable[3].description, 'ZZZ')
    

class EntriesWithReconciliationDate(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('05/01/2010')
        self.add_entry('05/01/2010')
        self.etable[1].reconciliation_date = '05/01/2010'
        self.etable.save_edits()
    
    def test_sort_by_reconciliation_date(self):
        # Don't crash because some dates are None.
        self.etable.sort_by('reconciliation_date') # no crash
        eq_(self.etable[0].reconciliation_date, '')
        eq_(self.etable[1].reconciliation_date, '05/01/2010')
    

class TwoBudgetsWithOneNoneStopDate(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('expense', account_type=EXPENSE)
        self.add_budget('expense', None, '42', stop_date=None)
        self.add_budget('expense', None, '42', stop_date='21/12/2012')
    
    def test_sort_by_stop_date(self):
        # Don't crash because some dates are None.
        self.btable.sort_by('stop_date') # no crash
        eq_(self.btable[0].stop_date, '')
        eq_(self.btable[1].stop_date, '21/12/2012')
    

class TwoSchedulesWithOneNoneStopDate(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_schedule(stop_date=None)
        self.add_schedule(stop_date='21/12/2012')
    
    def test_sort_by_stop_date(self):
        # Don't crash because some dates are None.
        self.sctable.sort_by('stop_date') # no crash
        eq_(self.sctable[0].stop_date, '')
        eq_(self.sctable[1].stop_date, '21/12/2012')
    

class TwoTransactionsWithDifferentCurrencies(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_txn(amount='42 GBP')
        self.add_txn(amount='43 CAD')
    
    def test_sort_by_amount(self):
        # When sorting by amount, just use the raw number as a sort key. Ignore currencies.
        self.ttable.sort_by('amount') # no crash
        eq_(self.ttable[0].amount, 'GBP 42.00')
        eq_(self.ttable[1].amount, 'CAD 43.00')
    

class MixedUpReconciledScheduleAndBudget(TestCase):
    # A mix of 4 txns. One reconciled, one normal, one schedule spawn and one budget spawn.
    def setUp(self):
        self.mock_today(2010, 1, 1)
        self.create_instances()
        self.document.select_month_range() # we just want 4 transactions
        self.add_account('expense', account_type=EXPENSE)
        self.add_account('asset')
        self.document.show_selected_account()
        self.add_entry('02/01/2010', description='reconciled')
        self.etable[0].reconciliation_date = '02/01/2010'
        self.etable.save_edits()
        self.add_txn('01/01/2010', description='plain', from_='asset')
        self.add_schedule(repeat_type_index=2, description='schedule', account='asset', amount='42') # monthly
        self.add_budget('expense', 'asset', '500', start_date='01/01/2010')
    
    def test_sort_etable_by_status(self):
        # Reconciled are first, then plain, then schedules, then budgets
        self.mainwindow.select_entry_table() # 'asset' is already selected from setup
        self.etable.sort_by('status')
        eq_(self.etable[0].description, 'reconciled')
        eq_(self.etable[1].description, 'plain')
        eq_(self.etable[2].description, 'schedule')
        assert self.etable[3].is_budget
    
    def test_sort_ttable_by_status(self):
        # Reconciled are first, then plain, then schedules, then budgets
        self.mainwindow.select_transaction_table()
        self.ttable.sort_by('status')
        eq_(self.ttable[0].description, 'reconciled')
        eq_(self.ttable[1].description, 'plain')
        eq_(self.ttable[2].description, 'schedule')
        assert self.ttable[3].is_budget
    

class TwoTransactionsAddedWhenSortedByDescription(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_transaction_table()
        self.ttable.sort_by('description')
        self.add_txn(description='foo', from_='asset')
        self.add_txn(description='bar', from_='asset')
    
    def test_sort_etable_by_description_then_by_date(self):
        # Like with ttable, etable doesn't ignore txn position when sorting by date.
        self.show_account('asset')
        self.etable.sort_by('description')
        self.etable.sort_by('date')
        eq_(self.etable[0].description, 'foo')
        eq_(self.etable[1].description, 'bar')
    
    def test_sort_ttable_by_date(self):
        # When sorting by date, the "position" attribute of the transaction is taken into account
        # when transactions have the same date.
        self.ttable.sort_by('date')
        eq_(self.ttable[0].description, 'foo')
        eq_(self.ttable[1].description, 'bar')
    
    def test_sort_order_persistent(self):
        # When changing transactions, the table is re-sorted automatically according to the current
        # sorting.
        eq_(self.ttable[0].description, 'bar')
        eq_(self.ttable[1].description, 'foo')
    
