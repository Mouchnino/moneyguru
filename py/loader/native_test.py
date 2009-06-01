# Unit Name: moneyguru.loader.native_test
# Created By: Virgil Dupras
# Created On: 2008-02-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from StringIO import StringIO
import os.path as op
from datetime import date

from hsutil.currency import USD, PLN

from ..exception import FileFormatError
from ..main_test import TestCase
from ..model.account import EXPENSE
from ..model.amount import Amount
from . import native


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
        self.loader.parse(self.filepath('xml', 'moneyguru.xml'))
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
        self.assertEqual(account.type, EXPENSE)
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 4)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2008, 2, 16))
        self.assertEqual(transaction.description, 'Entry 2')
        self.assertEqual(transaction.payee, 'Some Payee')
        self.assertEqual(transaction.checkno, '42')
        self.assertEqual(transaction.transfer, None)
        self.assertEqual(transaction.mtime, 1203095456)
        self.assertEqual(len(transaction.splits), 1)
        split = transaction.splits[0]
        self.assertEqual(split.account.name, 'Account 1')
        self.assertEqual(split.amount, Amount(-14, USD))
        transaction = transactions[1]
        self.assertEqual(transaction.date, date(2008, 2, 15))
        self.assertEqual(transaction.description, 'Entry 1')
        self.assertEqual(transaction.mtime, 1203095441)
        self.assertEqual(len(transaction.splits), 2)
        split = transaction.splits[0]
        self.assertEqual(split.account.name, 'Account 1')
        self.assertEqual(split.amount, Amount(42, USD))
        split = transaction.splits[1]
        self.assertEqual(split.account.name, 'foobar')
        self.assertEqual(split.amount, Amount(-42, USD))
        transaction = transactions[2]
        self.assertEqual(transaction.date, date(2008, 2, 12))
        self.assertEqual(transaction.description, 'Entry 3')
        self.assertEqual(transaction.transfer, None)
        self.assertEqual(transaction.mtime, 1203095473)
        self.assertEqual(len(transaction.splits), 1)
        split = transaction.splits[0]
        self.assertEqual(split.account.name, 'Account 2')
        self.assertEqual(split.amount, Amount(89, PLN))
        transaction = transactions[3]
        self.assertEqual(transaction.date, date(2008, 2, 19))
        self.assertEqual(transaction.description, 'Entry 4')
        self.assertEqual(transaction.transfer, None)
        self.assertEqual(transaction.mtime, 1203095497)
        split = transaction.splits[0]
        self.assertEqual(split.account.name, 'Account 2')
        self.assertEqual(split.amount, Amount(-101, PLN))
    
