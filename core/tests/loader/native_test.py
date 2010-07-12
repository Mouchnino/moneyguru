# Created By: Virgil Dupras
# Created On: 2008-02-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from StringIO import StringIO
from datetime import date

from nose.tools import eq_

from hscommon.currency import USD, PLN

from ..base import TestCase
from ...exception import FileFormatError
from ...loader import native
from ...model.account import AccountType
from ...model.amount import Amount


class NativeLoader(TestCase):
    def setUp(self):
        self.loader = native.Loader(USD)
    
    def test_parse_non_xml(self):
        content = 'this is not xml content'
        self.assertRaises(FileFormatError, self.loader._parse, StringIO(content))
    
    def test_parse_wrong_root_name(self):
        content = '<foobar></foobar>'
        self.assertRaises(FileFormatError, self.loader._parse, StringIO(content))
    
    def test_parse_minimal(self):
        content = '<moneyguru-file></moneyguru-file>'
        try:
            self.loader._parse(StringIO(content))
        except FileFormatError:
            self.fail()
    
    def test_wrong_date(self):
        # these used to raise FileFormatError, but now, we just want to make sure that there is no
        # crash.
        content = '<moneyguru-file><transaction date="bobsleigh" /></moneyguru-file>'
        self.loader._parse(StringIO(content))
        self.loader.load() # no crash

    def test_wrong_mtime(self):
        # these used to raise FileFormatError, but now, we just want to make sure that there is no
        # crash.
        content = '<moneyguru-file><transaction date="2008-01-01" mtime="abc" /></moneyguru-file>'
        self.loader._parse(StringIO(content))
        self.loader.load() # no crash

    def test_account_and_entry_values(self):
        """Make sure loaded values are correct"""
        self.loader.parse(self.filepath('moneyguru', 'simple.moneyguru'))
        self.loader.load()
        accounts = self.loader.accounts
        self.assertEqual(len(accounts), 3)
        account = accounts[0]
        self.assertEqual(account.name, 'Account 1')
        self.assertEqual(account.currency, USD)
        account = accounts[1]
        self.assertEqual(account.name, 'Account 2')
        self.assertEqual(account.currency, PLN)
        account = accounts[2]
        self.assertEqual(account.name, 'foobar')
        self.assertEqual(account.currency, USD)
        self.assertEqual(account.type, AccountType.Expense)
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 4)
        transaction = transactions[0]
        eq_(transaction.date, date(2008, 2, 12))
        eq_(transaction.description, 'Entry 3')
        eq_(transaction.transfer, None)
        eq_(transaction.mtime, 1203095473)
        eq_(len(transaction.splits), 1)
        split = transaction.splits[0]
        eq_(split.account.name, 'Account 2')
        eq_(split.amount, Amount(89, PLN))
        
        transaction = transactions[1]
        eq_(transaction.date, date(2008, 2, 15))
        eq_(transaction.description, 'Entry 1')
        eq_(transaction.mtime, 1203095441)
        eq_(len(transaction.splits), 2)
        split = transaction.splits[0]
        eq_(split.account.name, 'Account 1')
        eq_(split.amount, Amount(42, USD))
        split = transaction.splits[1]
        eq_(split.account.name, 'foobar')
        eq_(split.amount, Amount(-42, USD))
        
        transaction = transactions[2]
        eq_(transaction.date, date(2008, 2, 16))
        eq_(transaction.description, 'Entry 2')
        eq_(transaction.payee, 'Some Payee')
        eq_(transaction.checkno, '42')
        eq_(transaction.transfer, None)
        eq_(transaction.mtime, 1203095456)
        eq_(len(transaction.splits), 1)
        split = transaction.splits[0]
        self.assertEqual(split.account.name, 'Account 1')
        self.assertEqual(split.amount, Amount(-14, USD))
        
        transaction = transactions[3]
        eq_(transaction.date, date(2008, 2, 19))
        eq_(transaction.description, 'Entry 4')
        eq_(transaction.transfer, None)
        eq_(transaction.mtime, 1203095497)
        split = transaction.splits[0]
        eq_(split.account.name, 'Account 2')
        eq_(split.amount, Amount(-101, PLN))
    
