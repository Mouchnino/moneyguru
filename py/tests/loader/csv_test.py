# Unit Name: moneyguru.loader.csv_test
# Created By: Virgil Dupras
# Created On: 2009-01-18
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date

from hsutil.currency import USD, EUR
from hsutil.misc import allsame

from ..base import TestCase
from ...exception import FileFormatError
from ...loader.csv_ import (Loader, CSV_DATE, CSV_DESCRIPTION, CSV_PAYEE, CSV_CHECKNO, CSV_TRANSFER, 
    CSV_AMOUNT, CSV_CURRENCY, CSV_REFERENCE)
from ...model.amount import Amount

class Pristine(TestCase):
    def setUp(self):
        self.loader = Loader(USD)
    
    def test_fortis(self):
        # a fortis csv import. ';' delimiter, with headers.
        self.loader.parse(self.filepath('csv/fortis.csv'))
        # there are blank lines, but they have been stripped out
        self.assertEqual(len(self.loader.lines), 19)
        self.assertEqual(len(self.loader.lines[0]), 8)
        # the lines below until the load() are the equivalent of the user linking columns with fields
        # and removing the first line.
        self.loader.column_indexes[CSV_DATE] = 1
        self.loader.column_indexes[CSV_DESCRIPTION] = 5
        self.loader.column_indexes[CSV_AMOUNT] = 3
        self.loader.column_indexes[CSV_CURRENCY] = 4
        self.loader.column_indexes[CSV_REFERENCE] = 0
        self.loader.lines = self.loader.lines[1:]
        self.loader.load()
        self.assertEqual(len(self.loader.accounts), 1)
        [account] = self.loader.accounts
        self.assertEqual(account.name, 'CSV Import')
        transactions = self.loader.transactions
        self.assertEqual(len(transactions), 18)
        txn = transactions[0]
        self.assertEqual(txn.date, date(2008, 12, 1))
        self.assertEqual(txn.description, 'RETRAIT A UN DISTRIBUTEUR FORTIS')
        self.assertEqual(txn.splits[0].account.name, 'CSV Import')
        self.assertEqual(txn.splits[0].amount, Amount(-100, EUR))
        self.assertTrue(txn.splits[1].account is None)
        self.assertEqual(txn.splits[1].amount, Amount(100, EUR))
        self.assertEqual(txn.splits[0].reference, '2008-0069')
    
    def test_lots_of_noise(self):
        # this file has 4 lines of non-separated header (Sniffer doesn't work) and a footer
        self.loader.parse(self.filepath('csv/lots_of_noise.csv'))
        self.assertTrue(allsame(len(line) for line in self.loader.lines))
    
    def test_no_transactions(self):
        # a Deutsch Bank export without transactions in it. It would raise an error during sniffing
        self.assertRaises(FileFormatError, self.loader.parse, self.filepath('csv/no_transaction.csv'))
    
