# Unit Name: moneyguru.loader.base_test
# Created By: Virgil Dupras
# Created On: 2008-02-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date, datetime

from hsutil.testcase import TestCase

from ...loader import base

class Pristine(TestCase):
    def setUp(self):
        self.loader = base.Loader('USD')
    
    def test_accounts(self):
        self.assertEqual(len(self.loader.account_infos), 0)
    
    def test_unnamed_account(self):
        """Name is mandatory"""
        self.loader.start_account()
        self.loader.flush_account()
        self.assertEqual(len(self.loader.account_infos), 0)
    
    def test_default_currency(self):
        """Currency is optional"""
        self.loader.start_account()
        self.loader.account_info.name = 'foo'
        self.loader.flush_account()
        self.assertEqual(len(self.loader.account_infos), 1)
        self.assertTrue(self.loader.account_infos[0].currency is None)
    

class OneAccount(TestCase):
    def setUp(self):
        self.loader = base.Loader('USD')
        self.loader.parse_date = lambda rawdate: datetime.strptime(rawdate, '%Y/%m/%d').date()
        self.loader.start_account()
        self.loader.account_info.name = 'foo'
    
    def test_missing_amount(self):
        """Amount is mandatory"""
        self.loader.start_transaction()
        self.loader.transaction_info.date = '2008/02/15'
        self.loader.transaction_info.description = 'foo'
        self.loader.transaction_info.transfer = 'bar'
        self.loader.flush_account()
        self.assertEqual(len(self.loader.transaction_infos), 0)
    
    def test_missing_date(self):
        """Date is mandatory"""
        self.loader.start_transaction()
        self.loader.transaction_info.amount = '42'
        self.loader.transaction_info.description = 'foo'
        self.loader.transaction_info.transfer = 'bar'
        self.loader.flush_account()
        self.assertEqual(len(self.loader.transaction_infos), 0)
    
    def test_missing_description(self):
        """Description is optional"""
        self.loader.start_transaction()
        self.loader.transaction_info.date = '2008/02/15'
        self.loader.transaction_info.amount = '42'
        self.loader.transaction_info.transfer = 'bar'
        self.loader.flush_account()
        self.assertEqual(len(self.loader.transaction_infos), 1)
    
    def test_missing_transfer(self):
        """Category is optional"""
        self.loader.start_transaction()
        self.loader.transaction_info.date = date(2008, 2, 15)
        self.loader.transaction_info.amount = '42'
        self.loader.transaction_info.description = 'foo'
        self.loader.flush_account()
        self.assertEqual(len(self.loader.transaction_infos), 1)
        # But the balancing entry in the imbalance account
        self.assertEqual(len(self.loader.account_infos), 1)
    
