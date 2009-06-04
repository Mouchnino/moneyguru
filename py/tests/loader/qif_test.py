# Unit Name: moneyguru.loader.qif_test
# Created By: Virgil Dupras
# Created On: 2008-02-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import os.path as op
from datetime import date

from hsutil.currency import USD

from ..base import TestCase
from ...loader.qif import Loader
from ...model.account import LIABILITY
from ...model.amount import Amount

class Pristine(TestCase):
    def setUp(self):
        self.loader = Loader(USD)
    
    def test_checkbook_values(self):
        self.loader.parse(self.filepath('qif', 'checkbook.qif'))
        self.loader.load()
        accounts = [a for a in self.loader.accounts if a.is_balance_sheet_account()]
        # Assets
        self.assertEqual(len(accounts), 2)
        account = accounts[0]
        self.assertEqual(account.name, 'Account 1')
        self.assertEqual(account.currency, USD)
        account = accounts[1]
        self.assertEqual(account.name, 'Account 2')
        self.assertEqual(account.currency, USD)
        transactions = self.loader.transactions
        self.assertEqual(len(transactions), 8)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 1, 1))
        self.assertEqual(transaction.description, 'Starting Balance')
        self.assertEqual(transaction.payee, '')
        self.assertEqual(transaction.splits[0].account.name, 'Account 1')
        self.assertEqual(transaction.splits[0].amount, Amount(42.32, USD))
        self.assertTrue(transaction.splits[1].account is None)
        self.assertEqual(transaction.splits[1].amount, Amount(-42.32, USD))
        transaction = transactions[1]
        self.assertEqual(transaction.date, date(2007, 1, 1))
        self.assertEqual(transaction.description, 'Deposit')
        self.assertEqual(transaction.payee, '')
        self.assertEqual(transaction.splits[0].account.name, 'Account 1')
        self.assertEqual(transaction.splits[0].amount, Amount(100, USD))
        self.assertEqual(transaction.splits[1].account.name, 'Salary')
        self.assertEqual(transaction.splits[1].amount, Amount(-100, USD))
        transaction = transactions[2]
        self.assertEqual(transaction.date, date(2007, 1, 1))
        self.assertEqual(transaction.description, 'Starting Balance')
        self.assertEqual(transaction.payee, '')
        self.assertEqual(transaction.splits[0].account.name, 'Account 2')
        self.assertEqual(transaction.splits[0].amount, Amount(3000, USD))
        self.assertTrue(transaction.splits[1].account is None)
        self.assertEqual(transaction.splits[1].amount, Amount(-3000, USD))
        transaction = transactions[3]
        self.assertEqual(transaction.date, date(2007, 1, 2))
        self.assertEqual(transaction.description, 'Withdrawal')
        self.assertEqual(transaction.payee, '')
        self.assertEqual(transaction.splits[0].account.name, 'Account 1')
        self.assertEqual(transaction.splits[0].amount, Amount(-60, USD))
        self.assertEqual(transaction.splits[1].account.name, 'Cash')
        self.assertEqual(transaction.splits[1].amount, Amount(60, USD))
        transaction = transactions[4]
        self.assertEqual(transaction.date, date(2007, 1, 2))
        self.assertEqual(transaction.description, 'Power Bill')
        self.assertEqual(transaction.payee, 'Hydro-Quebec')
        self.assertEqual(transaction.splits[0].account.name, 'Account 1')
        self.assertEqual(transaction.splits[0].amount, Amount(-57.12, USD))
        self.assertEqual(transaction.splits[1].account.name, 'Utilities')
        self.assertEqual(transaction.splits[1].amount, Amount(57.12, USD))
        transaction = transactions[5]
        self.assertEqual(transaction.date, date(2007, 1, 5))
        self.assertEqual(transaction.description, 'Interest')
        self.assertEqual(transaction.payee, 'My Bank')
        self.assertEqual(transaction.splits[0].account.name, 'Account 2')
        self.assertEqual(transaction.splits[0].amount, Amount(8.92, USD))
        self.assertEqual(transaction.splits[1].account.name, 'Interest')
        self.assertEqual(transaction.splits[1].amount, Amount(-8.92, USD))
        transaction = transactions[6]
        self.assertEqual(transaction.date, date(2007, 2, 4))
        self.assertEqual(transaction.description, 'Transfer')
        self.assertEqual(transaction.payee, 'Account 2')
        self.assertEqual(transaction.splits[0].account.name, 'Account 1')
        self.assertEqual(transaction.splits[0].amount, Amount(80.00, USD))
        self.assertTrue(transaction.splits[1].account is None)
        self.assertEqual(transaction.splits[1].amount, Amount(-80.00, USD))
        transaction = transactions[7]
        self.assertEqual(transaction.date, date(2007, 2, 4))
        self.assertEqual(transaction.description, 'Transfer')
        self.assertEqual(transaction.payee, 'Account 1')
        self.assertEqual(transaction.splits[0].account.name, 'Account 2')
        self.assertEqual(transaction.splits[0].amount, Amount(-80.00, USD))
        self.assertTrue(transaction.splits[1].account is None)
        self.assertEqual(transaction.splits[1].amount, Amount(80.00, USD))
    
    def test_missing_values(self):
        self.loader.parse(self.filepath('qif', 'missing_fields.qif'))
        self.loader.load()
        accounts = [a for a in self.loader.accounts if a.is_balance_sheet_account()]
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        self.assertEqual(account.name, 'Account')
        self.assertEqual(account.currency, USD)
        transactions = self.loader.transactions
        self.assertEqual(len(transactions), 3)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 1, 1))
        self.assertEqual(transaction.description, 'Complete Entry')
        self.assertEqual(transaction.splits[0].account.name, 'Account')
        self.assertEqual(transaction.splits[0].amount, Amount(100.00, USD))
        self.assertEqual(transaction.splits[1].account.name, 'Category')
        self.assertEqual(transaction.splits[1].amount, Amount(-100.00, USD))
        transaction = transactions[1]
        self.assertEqual(transaction.date, date(2007, 1, 2))
        self.assertEqual(transaction.description, 'No Category')
        self.assertEqual(transaction.splits[0].account.name, 'Account')
        self.assertEqual(transaction.splits[0].amount, Amount(100.00, USD))
        self.assertTrue(transaction.splits[1].account is None)
        self.assertEqual(transaction.splits[1].amount, Amount(-100.00, USD))
        transaction = transactions[2]
        self.assertEqual(transaction.date, date(2007, 1, 4))
        self.assertEqual(transaction.description, '')
        self.assertEqual(transaction.splits[0].account.name, 'Account')
        self.assertEqual(transaction.splits[0].amount, Amount(100.00, USD))
        self.assertEqual(transaction.splits[1].account.name, 'Category')
        self.assertEqual(transaction.splits[1].amount, Amount(-100.00, USD))
    
    def test_four_digit_year(self):
        self.loader.parse(self.filepath('qif', 'four_digit_year.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 1, 1))
    
    def test_ddmmyy(self):
        self.loader.parse(self.filepath('qif', 'ddmmyy.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 1, 22))
    
    def test_ddmmyyyy(self):
        self.loader.parse(self.filepath('qif', 'ddmmyyyy.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 1, 22))
    
    def test_ddmmyyyy_with_dots(self):
        self.loader.parse(self.filepath('qif', 'ddmmyyyy_with_dots.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 1, 22))
    
    def test_yyyymmdd_without_sep(self):
        self.loader.parse(self.filepath('qif', 'yyyymmdd_without_sep.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 1, 22))
    
    def test_chr13_line_sep(self):
        self.loader.parse(self.filepath('qif', 'chr13_line_sep.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        transactions = self.loader.transaction_infos
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2007, 2, 27))
    
    def test_first_field_not_account(self):
        # Previously, when the first field was not an account, a dummy "Account" field was added
        self.loader.parse(self.filepath('qif', 'first_field_not_account.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
    
    def test_accountless_with_splits(self):
        # Previously, the split amounts would be reversed
        self.loader.parse(self.filepath('qif', 'accountless_with_splits.qif'))
        self.loader.load()
        accounts = [a for a in self.loader.accounts if a.is_balance_sheet_account()]
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        self.assertEqual(account.name, 'Account')
        self.assertEqual(account.currency, USD)
        transactions = self.loader.transactions
        self.assertEqual(len(transactions), 2)
        transaction = transactions[0]
        self.assertEqual(transaction.date, date(2008, 8, 28))
        self.assertEqual(transaction.description, 'You\'ve got a payment')
        self.assertEqual(transaction.payee, 'Virgil Dupras')
        self.assertEqual(len(transaction.splits), 3)
        transaction = transactions[1]
        self.assertEqual(len(transaction.splits), 3)
    
    def test_other_sections(self):
        # Previously, other sections would confuse the qif loader
        self.loader.parse(self.filepath('qif', 'other_sections.qif'))
        self.loader.load()
        self.assertEqual(len(self.loader.transactions), 3)
    
    def test_missing_line_sep(self):
        # It is possible sometimes that some apps do bad exports that contain some missing line 
        # separators Make sure that it doesn't prevent the QIF from being loaded
        self.loader.parse(self.filepath('qif', 'missing_line_sep.qif'))
        self.loader.load()
        self.assertEqual(len(self.loader.transactions), 1)
        self.assertEqual(self.loader.transactions[0].splits[0].amount, Amount(42.32, USD))
    
    def test_credit_card(self):
        # A CCard account is imported as a liability
        self.loader.parse(self.filepath('qif', 'credit_card.qif'))
        self.loader.load()
        accounts = self.loader.account_infos
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        self.assertEqual(account.type, LIABILITY)
    
    def test_autoswitch(self):
        # autoswitch.qif has an autoswitch section with accounts containing "D" lines
        self.loader.parse(self.filepath('qif', 'autoswitch.qif'))
        self.loader.load()
        self.assertEqual(len(self.loader.account_infos), 51)
        self.assertEqual(len(self.loader.transaction_infos), 37)
    
    def test_autoswitch_buggy(self):
        # sp,eQIF exporter put another !Option:AutoSwitch after having cleared it
        self.loader.parse(self.filepath('qif', 'autoswitch_buggy.qif'))
        self.loader.load()
        self.assertEqual(len(self.loader.account_infos), 51)
        self.assertEqual(len(self.loader.transaction_infos), 37)
    
    def test_with_cat(self):
        # some file have a "!Type:Cat" section with buggy "D" lines
        self.loader.parse(self.filepath('qif', 'with_cat.qif'))
        self.loader.load()
        self.assertEqual(len(self.loader.account_infos), 1)
        self.assertEqual(len(self.loader.transaction_infos), 1)
    

class TransferBetweenAssets(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('first')
        self.add_account('second')
        self.add_entry(date='03/01/2009', description='transfer', transfer='first', increase='42')
    
    def test_save_to_qif(self):
        # When there's a transfer between 2 assets, only put an entry in one of the accounts
        export_filename = unicode(self.tmppath() + 'export.qif')
        self.document.save_to_qif(export_filename)
        exported = open(export_filename).read()
        reference = open(self.filepath('qif', 'export_ref_transfer.qif')).read()
        self.assertEqual(exported, reference)
    
