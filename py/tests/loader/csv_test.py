# Created By: Virgil Dupras
# Created On: 2009-01-18
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

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
        eq_(len(self.loader.lines), 19)
        eq_(len(self.loader.lines[0]), 8)
        # the lines below until the load() are the equivalent of the user linking columns with fields
        # and removing the first line.
        self.loader.column_indexes[CSV_DATE] = 1
        self.loader.column_indexes[CSV_DESCRIPTION] = 5
        self.loader.column_indexes[CSV_AMOUNT] = 3
        self.loader.column_indexes[CSV_CURRENCY] = 4
        self.loader.column_indexes[CSV_REFERENCE] = 0
        self.loader.lines = self.loader.lines[1:]
        self.loader.load()
        eq_(len(self.loader.accounts), 1)
        [account] = self.loader.accounts
        eq_(account.name, 'CSV Import')
        transactions = self.loader.transactions
        eq_(len(transactions), 18)
        txn = transactions[0]
        eq_(txn.date, date(2008, 12, 1))
        eq_(txn.description, 'RETRAIT A UN DISTRIBUTEUR FORTIS')
        eq_(txn.splits[0].account.name, 'CSV Import')
        eq_(txn.splits[0].amount, Amount(-100, EUR))
        self.assertTrue(txn.splits[1].account is None)
        eq_(txn.splits[1].amount, Amount(100, EUR))
        eq_(txn.splits[0].reference, '2008-0069')
    
    def test_fortis_with_r_linesep(self):
        # Same as fortis.csv, but instead of being \r\n lineseps, it's \r only
        self.loader.parse(self.filepath('csv/fortis_with_r_linesep.csv'))
        eq_(len(self.loader.lines), 19) # no crash
    
    def test_lots_of_noise(self):
        # this file has 4 lines of non-separated header (Sniffer doesn't work) and a footer
        self.loader.parse(self.filepath('csv/lots_of_noise.csv'))
        self.assertTrue(allsame(len(line) for line in self.loader.lines))
    
    def test_no_transactions(self):
        # a Deutsch Bank export without transactions in it. It would raise an error during sniffing
        self.assertRaises(FileFormatError, self.loader.parse, self.filepath('csv/no_transaction.csv'))
    
    def test_with_comments(self):
        # the 'comments.csv' file has lines starting with '#' which the parser had problems with.
        self.loader.parse(self.filepath('csv/comments.csv')) # no exception
        # It's not because the commented lines weren't passed to the sniffer that they don't show
        # up in the csv options panel. All lines must be there.
        eq_(len(self.loader.lines), 6)
    
