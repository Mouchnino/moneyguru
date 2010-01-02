# Created By: Virgil Dupras
# Created On: 2008-06-22
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import time
import xmlrpclib
from datetime import date

from nose.tools import eq_

from hsutil import io
from hsutil.currency import Currency, USD, PLN, EUR, CAD, XPF
from hsutil.decorators import log_calls

from .base import ApplicationGUI, TestCase, TestSaveLoadMixin
from .model.currency_test import FakeServer
from ..app import Application
from ..model import currency
from ..model.account import INCOME, LIABILITY
from ..model.currency import RatesDB
from ..model.date import MonthRange

class TestCase(TestCase):
    def superSetUp(self):
        # For these tests, we actually want the rates db to hit a fake server, so we override superSetUp
        # During tests, we don't want the rates db to hit the currency server
        self.mock(xmlrpclib, 'ServerProxy', FakeServer)
        Currency.set_rates_db(RatesDB(':memory:', False)) # async
        self.mock(currency, 'initialize_db', lambda path: None)
    

class NoSetup(TestCase):
    def test_cache_path_is_auto_created(self):
        """the cache_path directory is automatically created"""
        cache_path = self.tmppath() + 'foo/bar'
        app = Application(ApplicationGUI(), cache_path=cache_path)
        self.assertTrue(io.exists(cache_path))
    
    def test_cache_path_is_none(self):
        """currency.initialize_db() is called with :memory: when cache_path is None"""
        self.mock(currency, 'initialize_db', log_calls(currency.initialize_db))
        app = Application(ApplicationGUI()) # default cache_path is None
        expected = [
            {'path': ':memory:'}
        ]
        self.assertEqual(currency.initialize_db.calls, expected)
    
    def test_cache_path_is_not_none(self):
        """currency.initialize_db() is called with cache_path/currency.db when cache_path is not None"""
        cache_path = self.tmppath()
        self.mock(currency, 'initialize_db', log_calls(currency.initialize_db))
        app = Application(ApplicationGUI(), cache_path=cache_path)
        expected = [
            {'path': cache_path + 'currency.db'}
        ]
        self.assertEqual(currency.initialize_db.calls, expected)
    
    def test_default_currency(self):
        """It's possible to specify a default currency at startup"""
        self.app = Application(ApplicationGUI(), default_currency=PLN)
        self.create_instances()
        self.mainwindow.select_transaction_table()
        self.assertEqual(self.app.default_currency, PLN)
        self.add_account_legacy()
        self.assertEqual(self.app.default_currency, PLN)
    

class OneEmptyAccountEUR(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('Checking', EUR)
        self.document.date_range = MonthRange(date(2007, 10, 1))
    
    def test_add_entry_with_foreign_amount(self):
        """Saving an entry triggers an ensure_rates"""
        log = []
        FakeServer.hooklog(log)
        self.add_entry('20/5/2008', increase='12 usd')
        # A request is made for both the amount that has just been written and the account of the entry
        expected = set([
            (date(2008, 5, 20), date.today(), 'USD'),
            (date(2008, 5, 20), date.today(), 'EUR'),
        ])
        self.assertEqual(set(log), expected)
    
    def test_add_transaction_with_foreign_amount(self):
        """Saving an entry triggers an ensure_rates"""
        log = []
        FakeServer.hooklog(log)
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        self.ttable.edited.date = '20/5/2008'
        self.ttable.edited.amount = '12 eur'
        self.ttable.save_edits()
        # A request is made for both the amount that has just been written and the account of the entry
        expected = set([
            (date(2008, 5, 20), date.today(), 'EUR'),
            (date(2008, 5, 20), date.today(), 'USD'),
        ])
        self.assertEqual(set(log), expected)
    

class CADAssetAndUSDAsset(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('CAD Account', CAD)
        self.add_account_legacy('USD Account', USD)
    
    def test_make_amount_native(self):
        # Making an amount native when the both sides are asset/liability creates a MCT
        # First, let's add a 'native' transaction
        self.add_entry(transfer='CAD Account', increase='42 usd')
        # Then, make the other side 'native'
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.decrease = '40 cad'
        self.etable.save_edits()
        # The other side should have *not* followed
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].increase, '42.00')
    

class CADLiabilityAndUSDLiability(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('CAD Account', CAD, account_type=LIABILITY)
        self.add_account_legacy('USD Account', USD, account_type=LIABILITY)
    
    def test_make_amount_native(self):
        # Making an amount native when the both sides are asset/liability creates a MCT
        # First, let's add a 'native' transaction
        self.add_entry(transfer='CAD Account', increase='42 usd')
        # Then, make the other side 'native'
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.liabilities[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.decrease = '40 cad'
        self.etable.save_edits()
        # The other side should have *not* followed
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.liabilities[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].increase, '42.00')
    

class EntryWithForeignCurrencyAmount(TestCase):
    """2 accounts (including one income), one entry. The entry has an amount that differs from the 
    account's currency. The rates db is mocked.
    """
    def setUp(self):
        self.create_instances()
        Currency.set_rates_db(RatesDB())
        EUR.set_CAD_value(1.42, date(2007, 10, 1))
        PLN.set_CAD_value(0.42, date(2007, 10, 1))
        self.add_account_legacy('first', CAD)
        self.add_account_legacy('second', PLN, account_type=INCOME)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.add_entry(date='1/10/2007', transfer='second', increase='42 eur')
        self.document.date_range = MonthRange(date(2007, 10, 1))
    
    def test_bar_graph_data(self):
        """The amount shown in the bar graph is a converted amount"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.bar_graph_data(), [('01/10/2007', '08/10/2007', '%2.2f' % ((42 * 1.42) / 0.42), '0.00')])
    
    def test_ensures_rates(self):
        """Upon calling save and load, rates are asked for both EUR and PLN"""
        rates_db = Currency.get_rates_db()
        self.mock(rates_db, 'ensure_rates', log_calls(rates_db.ensure_rates))
        filename = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(filename)
        self.document.load_from_xml(filename)
        calls = rates_db.ensure_rates.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(set(calls[0]['currencies']), set(['PLN', 'EUR', 'CAD']))
        self.assertEqual(calls[0]['start_date'], date(2007, 10, 1))
    
    def test_entry_balance(self):
        """The entry's balance is correctly incremented (using the exchange rate)"""
        self.assertEqual(self.etable[0].balance, 'CAD %2.2f' % (42 * 1.42))
    
    def test_opposite_entry_balance(self):
        """The 'other side' of the entry also have its balance correctly computed"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[0].balance, 'PLN %2.2f' % ((42 * 1.42) / 0.42))
    

class CADAssetAndUSDIncome(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('CAD Account', CAD)
        self.add_account_legacy('USD Income', USD, account_type=INCOME)
        self.add_entry(transfer='CAD Account', increase='42 usd')
    
    def test_make_amount_native(self):
        """Making an amount native when the other side is an income/expense never creates a MCT"""
        # First, let's add a 'native' transaction
        # Then, make the asset side 'native'
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.increase = '40 cad'
        self.etable.save_edits()
        # The other side should have followed
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[0].increase, 'CAD 40.00')
    

class DifferentCurrencies(TestCase, TestSaveLoadMixin):
    """2 accounts. One with the default app currency and the other with another currency.
    2 transactions. One with the default currency and one with a different currency. Both 
    transaction have a transfer to the second account.
    
    Mixed with TestSaveLoadMixin to make sure currency information is correctly saved/loaded
    """
    def setUp(self):
        self.app = Application(ApplicationGUI(), default_currency=CAD)
        self.create_instances()
        self.add_account_legacy('first account')
        self.add_account_legacy('second account', USD)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.add_entry(description='first entry', transfer='second account', increase='42 usd')
        self.add_entry(description='second entry', transfer='second account', increase='42 eur')
    
    def test_entries_amount(self):
        """All entries have the appropriate currency"""
        self.assertEqual(self.etable[0].increase, 'USD 42.00')
        self.assertEqual(self.etable[1].increase, 'EUR 42.00')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].decrease, 'USD 42.00')
        self.assertEqual(self.etable[1].decrease, 'EUR 42.00')
    

class ThreeCurrenciesTwoEntriesSaveLoad(TestCase):
    """Three account of different currencies, and 2 entries on differenet date. The app is saved, 
    and then loaded (The goal of this is to test that moneyguru ensures it got the rates it needs).
    """ 
    def setUp(self):
        self.app = Application(ApplicationGUI(), default_currency=CAD)
        self.create_instances()
        self.add_account_legacy('first account')
        self.add_account_legacy('second account', USD)
        self.add_account_legacy('third account', EUR)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.add_entry(date='20/4/2008', increase='42 cad')
        self.add_entry(date='25/4/2008', increase='42 cad')
    
    def save_and_load(self):
        """Save the app somewhere, the loads it"""
        filename = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(filename)
        self.document.load_from_xml(filename)
    
    def test_ensures_rates(self):
        """Upon calling save and load, rates are asked for the 20-today range for both USD and EUR"""
        log = []
        FakeServer.hooklog(log)
        self.save_and_load()
        expected = set([
            (date(2008, 4, 20), date.today(), 'USD'), 
            (date(2008, 4, 20), date.today(), 'EUR'),
        ])
        self.assertEqual(set(log), expected)
        # Now let's test that the rates are in the DB
        self.assertEqual(USD.value_in(CAD, date(2008, 4, 20)), 1.42)
        self.assertEqual(EUR.value_in(CAD, date(2008, 4, 22)), 1.44)
        self.assertEqual(EUR.value_in(USD, date(2008, 4, 24)), 1.0)
        self.assertEqual(USD.value_in(CAD, date(2008, 4, 25)), 1.47)
        self.assertEqual(USD.value_in(CAD, date(2008, 4, 27)), 1.49)
    
    def test_ensures_rates_async(self):
        """ensure_rates() executes asynchronously"""
        # I can't think of any graceful way to test something like that, so I assume that if I make
        # the mocked get_CAD_values() to sleep for a little while, the next line after it in the test will
        # be executed first. If this test starts to fail randomly, we'll have to think about a better
        # way to test that (or increase the sleep time).
        old_func = FakeServer.get_CAD_values
        def mock_get_CAD_values(self, start, end, currency):
            time.sleep(0.05)
            return old_func(self, start, end, currency)
        
        self.mock(FakeServer, 'get_CAD_values', mock_get_CAD_values)
        rates_db = Currency.get_rates_db()
        self.mock(rates_db, 'async', True) # Turn async on
        self.save_and_load()
        # This is a weird way to test that we don't have the rate yet. No need to import fallback 
        # rates just for that.
        self.assertNotEqual(rates_db.get_rate(date(2008, 4, 20), 'USD', 'CAD'), 1.42)
        self.jointhreads()
        self.assertEqual(rates_db.get_rate(date(2008, 4, 20), 'USD', 'CAD'), 1.42)
    

class OneMCT(TestCase):
    """Two asset accounts, one MCT between the 2"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('CAD Account', CAD)
        self.add_account_legacy('USD Account', USD)
        self.add_entry(transfer='CAD Account', increase='42 usd')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.decrease = '40 cad'
        self.etable.save_edits()
    
    def test_add_imbalancing_split(self):
        """Adding a split making one of the two currencies balance, while leaving the rest all on 
        the same side makes moneyGuru rebalance this"""
        self.tpanel.load()
        self.stable.add()
        row = self.stable.selected_row
        row.credit = '42 usd'
        self.stable.save_edits() # Now we have CAD standing all alone
        self.assertEqual(len(self.stable), 4)
        self.assertEqual(self.stable[3].debit, 'CAD 40.00')
    
    def test_set_entry_increase(self):
        """If we set up the CAD side to be an increase, the USD side must switch to decrease"""
        # It's not because we changed the amount here that the USD side will have something else than 42
        row = self.etable.selected_row
        row.increase = '12 cad'
        self.etable.save_edits()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].decrease, '42.00')
    
    def test_set_split_to_logical_imbalance(self):
        """The first split is the USD entry (a debit). If we set it to be a credit instead, we end
        up with both splits on the same side. We must create balancing splits.
        """
        self.tpanel.load()
        row = self.stable.selected_row
        row.credit = '12 usd'
        self.stable.save_edits()
        self.assertEqual(len(self.stable), 4)
        expected = set(['12.00', 'CAD 40.00'])
        self.assertTrue(self.stable[2].debit in expected)
        self.assertTrue(self.stable[3].debit in expected)
    

class EntryWithXPFAmount(TestCase):
    def setUp(self):
        self.create_instances()
        XPF.set_CAD_value(0.42, date(2009, 7, 20))
        self.add_account_legacy('account', CAD)
        self.add_entry('20/07/2009', increase='100 XPF')
    
    def test_account_balance_is_correct(self):
        # Because XPF has an exponent of 0, there was a bug where currency conversion wouldn't be
        # done correctly.
        eq_(self.etable[0].balance, 'CAD 42.00')
    
