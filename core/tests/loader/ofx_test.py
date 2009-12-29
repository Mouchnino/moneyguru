# coding=utf-8
# Created By: Eric Mc Sween
# Created On: 2008-02-11
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path
from datetime import date

from hsutil.currency import USD, CAD, EUR

from ..base import TestCase
from ...exception import FileFormatError
from ...loader import ofx
from ...model.amount import Amount

class NoSetup(TestCase):
    def test_dont_choke_on_empty_files(self):
        # The ofx loader doesn't choke on an empty file
        loader = ofx.Loader(USD)
        self.assertRaises(FileFormatError, loader.parse, self.filepath('zerofile'))
    

class Desjardins(TestCase):
    def setUp(self):
        loader = ofx.Loader(USD)
        loader.parse(self.filepath('ofx', 'desjardins.ofx'))
        loader.load()
        self.loader = loader

    def test_accounts(self):
        accounts = [(x.name, x.currency, str(x.balance)) for x in self.loader.account_infos]
        expected = [('815-30219-12345-EOP', 'CAD', '3925.84'), 
                    ('815-30219-54321-ES1', 'CAD', '0.00'),
                    ('815-30219-11111-EOP', 'USD', '3046.90'),]
        self.assertEqual(accounts, expected)

    def test_transactions_usd_account(self):
        account = self.loader.accounts.find('815-30219-11111-EOP')
        self.assertEqual(len(account.entries), 3)
        entry = account.entries[0]
        self.assertEqual(entry.date, date(2008, 1, 31))
        self.assertEqual(entry.description, u'Intérêt sur EOP/')
        self.assertEqual(entry.amount, Amount(0.02, USD))
        entry = account.entries[1]
        self.assertEqual(entry.date, date(2008, 2, 1))
        self.assertEqual(entry.description, u'Dépôt au comptoir/')
        self.assertEqual(entry.amount, Amount(5029.50, USD))
        entry = account.entries[2]
        self.assertEqual(entry.date, date(2008, 2, 1))
        self.assertEqual(entry.description, u'Retrait au comptoir/')
        self.assertEqual(entry.amount, Amount(-2665, USD))

    def test_reference(self):
        """OFX IDs are stored in the accounts and entries."""
        account = self.loader.accounts[0]
        self.assertEqual(account.reference, '700000100|0389347|815-30219-12345-EOP')
        transaction = self.loader.transaction_infos[0]
        self.assertEqual(transaction.reference, 'Th3DJACES')
    

class Invalid(TestCase):
    def test_format_error(self):
        loader = ofx.Loader(USD)
        self.assertRaises(FileFormatError, loader.parse, self.filepath('ofx', 'invalid.ofx'))


class ING(TestCase):
    def setUp(self):
        loader = ofx.Loader(USD)
        loader.parse(self.filepath('ofx', 'ing.qfx'))
        loader.load()
        self.loader = loader

    def test_accounts(self):
        accounts = [(x.name, x.currency) for x in self.loader.accounts]
        expected = [('123456', CAD)]
        self.assertEqual(accounts, expected)

    def test_entries(self):
        account = self.loader.accounts.find('123456')
        self.assertEqual(len(account.entries), 1)
        entry = account.entries[0]
        self.assertEqual(entry.date, date(2005, 9, 23))
        self.assertEqual(entry.description, u'Dépôt')
        self.assertEqual(entry.amount, Amount(100, CAD))

class InvalidCurrency(TestCase):
    def setUp(self):
        loader = ofx.Loader(USD)
        loader.parse(self.filepath('ofx', 'invalid_currency.ofx'))
        loader.load()
        self.loader = loader
    
    def test_amounts_in_invalid_currency_account(self):
        account = self.loader.accounts.find('815-30219-11111-EOP')
        self.assertEqual(len(account.entries), 3)
        entry = account.entries[0]
        self.assertEqual(entry.amount, Amount(0.02, USD))
    

class Fortis(TestCase):
    def setUp(self):
        loader = ofx.Loader(EUR)
        loader.parse(self.filepath('ofx', 'fortis.ofx'))
        loader.load()
        self.loader = loader
    
    def test_reference(self):
        # Fortis ofx files don't have a branch id. The reference should exist even without it.
        account = self.loader.accounts[0]
        self.assertEqual(account.reference, 'FORTIS||001-5587496-84')
        transaction = self.loader.transaction_infos[0]
        self.assertEqual(transaction.reference, '20080026')
    

class BlankFirstLine(TestCase):
    def setUp(self):
        loader = ofx.Loader(USD)
        loader.parse(self.filepath('ofx', 'blank_first_line.ofx'))
        loader.load()
        self.loader = loader
    
    def test_attrs(self):
        # Just make sure that a ofx file starting with a blank line is correctly loaded
        self.assertEqual(len(self.loader.accounts), 1)
        self.assertEqual(len(self.loader.transactions), 5)
    
