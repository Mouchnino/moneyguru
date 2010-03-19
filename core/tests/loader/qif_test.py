# Created By: Virgil Dupras
# Created On: 2008-02-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from hsutil.currency import USD
from hsutil.testutil import with_tmpdir

from ..base import TestApp, TestData
from ...loader.qif import Loader
from ...model.account import AccountType
from ...model.amount import Amount

def test_checkbook_values():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'checkbook.qif'))
    loader.load()
    accounts = [a for a in loader.accounts if a.is_balance_sheet_account()]
    # Assets
    eq_(len(accounts), 2)
    account = accounts[0]
    eq_(account.name, 'Account 1')
    eq_(account.currency, USD)
    account = accounts[1]
    eq_(account.name, 'Account 2')
    eq_(account.currency, USD)
    transactions = loader.transactions
    eq_(len(transactions), 8)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Starting Balance')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(42.32, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-42.32, USD))
    transaction = transactions[1]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Deposit')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(100, USD))
    eq_(transaction.splits[1].account.name, 'Salary')
    eq_(transaction.splits[1].amount, Amount(-100, USD))
    transaction = transactions[2]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Starting Balance')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 2')
    eq_(transaction.splits[0].amount, Amount(3000, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-3000, USD))
    transaction = transactions[3]
    eq_(transaction.date, date(2007, 1, 2))
    eq_(transaction.description, 'Withdrawal')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(-60, USD))
    eq_(transaction.splits[1].account.name, 'Cash')
    eq_(transaction.splits[1].amount, Amount(60, USD))
    transaction = transactions[4]
    eq_(transaction.date, date(2007, 1, 2))
    eq_(transaction.description, 'Power Bill')
    eq_(transaction.payee, 'Hydro-Quebec')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(-57.12, USD))
    eq_(transaction.splits[1].account.name, 'Utilities')
    eq_(transaction.splits[1].amount, Amount(57.12, USD))
    transaction = transactions[5]
    eq_(transaction.date, date(2007, 1, 5))
    eq_(transaction.description, 'Interest')
    eq_(transaction.payee, 'My Bank')
    eq_(transaction.splits[0].account.name, 'Account 2')
    eq_(transaction.splits[0].amount, Amount(8.92, USD))
    eq_(transaction.splits[1].account.name, 'Interest')
    eq_(transaction.splits[1].amount, Amount(-8.92, USD))
    transaction = transactions[6]
    eq_(transaction.date, date(2007, 2, 4))
    eq_(transaction.description, 'Transfer')
    eq_(transaction.payee, 'Account 2')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(80.00, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-80.00, USD))
    transaction = transactions[7]
    eq_(transaction.date, date(2007, 2, 4))
    eq_(transaction.description, 'Transfer')
    eq_(transaction.payee, 'Account 1')
    eq_(transaction.splits[0].account.name, 'Account 2')
    eq_(transaction.splits[0].amount, Amount(-80.00, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(80.00, USD))

def test_missing_values():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'missing_fields.qif'))
    loader.load()
    accounts = [a for a in loader.accounts if a.is_balance_sheet_account()]
    eq_(len(accounts), 1)
    account = accounts[0]
    eq_(account.name, 'Account')
    eq_(account.currency, USD)
    transactions = loader.transactions
    eq_(len(transactions), 3)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Complete Entry')
    eq_(transaction.splits[0].account.name, 'Account')
    eq_(transaction.splits[0].amount, Amount(100.00, USD))
    eq_(transaction.splits[1].account.name, 'Category')
    eq_(transaction.splits[1].amount, Amount(-100.00, USD))
    transaction = transactions[1]
    eq_(transaction.date, date(2007, 1, 2))
    eq_(transaction.description, 'No Category')
    eq_(transaction.splits[0].account.name, 'Account')
    eq_(transaction.splits[0].amount, Amount(100.00, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-100.00, USD))
    transaction = transactions[2]
    eq_(transaction.date, date(2007, 1, 4))
    eq_(transaction.description, '')
    eq_(transaction.splits[0].account.name, 'Account')
    eq_(transaction.splits[0].amount, Amount(100.00, USD))
    eq_(transaction.splits[1].account.name, 'Category')
    eq_(transaction.splits[1].amount, Amount(-100.00, USD))

def test_four_digit_year():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'four_digit_year.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 1))

def test_ddmmyy():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'ddmmyy.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_ddmmyyyy():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'ddmmyyyy.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_ddmmyyyy_with_dots():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'ddmmyyyy_with_dots.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_yyyymmdd_without_sep():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'yyyymmdd_without_sep.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_chr13_line_sep():
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'chr13_line_sep.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 2, 27))

def test_first_field_not_account():
    # Previously, when the first field was not an account, a dummy "Account" field was added
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'first_field_not_account.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)

def test_accountless_with_splits():
    # Previously, the split amounts would be reversed
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'accountless_with_splits.qif'))
    loader.load()
    accounts = [a for a in loader.accounts if a.is_balance_sheet_account()]
    eq_(len(accounts), 1)
    account = accounts[0]
    eq_(account.name, 'Account')
    eq_(account.currency, USD)
    transactions = loader.transactions
    eq_(len(transactions), 2)
    transaction = transactions[0]
    eq_(transaction.date, date(2008, 8, 28))
    eq_(transaction.description, 'You\'ve got a payment')
    eq_(transaction.payee, 'Virgil Dupras')
    eq_(len(transaction.splits), 3)
    transaction = transactions[1]
    eq_(len(transaction.splits), 3)

def test_other_sections():
    # Previously, other sections would confuse the qif loader
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'other_sections.qif'))
    loader.load()
    eq_(len(loader.transactions), 3)

def test_missing_line_sep():
    # It is possible sometimes that some apps do bad exports that contain some missing line 
    # separators Make sure that it doesn't prevent the QIF from being loaded
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'missing_line_sep.qif'))
    loader.load()
    eq_(len(loader.transactions), 1)
    eq_(loader.transactions[0].splits[0].amount, Amount(42.32, USD))

def test_credit_card():
    # A CCard account is imported as a liability
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'credit_card.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    eq_(account.type, AccountType.Liability)

def test_autoswitch():
    # autoswitch.qif has an autoswitch section with accounts containing "D" lines
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'autoswitch.qif'))
    loader.load()
    eq_(len(loader.account_infos), 50)
    eq_(len(loader.transaction_infos), 37)

def test_autoswitch_buggy():
    # sp,eQIF exporter put another !Option:AutoSwitch after having cleared it
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'autoswitch_buggy.qif'))
    loader.load()
    eq_(len(loader.account_infos), 50)
    eq_(len(loader.transaction_infos), 37)

def test_with_cat():
    # some file have a "!Type:Cat" section with buggy "D" lines
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'with_cat.qif'))
    loader.load()
    eq_(len(loader.account_infos), 1)
    eq_(len(loader.transaction_infos), 1)

def test_transfer():
    # Transfer happen with 2 entries putting [] brackets arround the account names of the 'L'
    # sections.
    loader = Loader(USD)
    loader.parse(TestData.filepath('qif', 'transfer.qif'))
    loader.load()
    eq_(len(loader.account_infos), 2)
    eq_(len(loader.transaction_infos), 1)

@with_tmpdir
def test_save_to_qif(tmppath):
    # When there's a transfer between 2 assets, only put an entry in one of the accounts
    app = TestApp()
    app.add_account('first')
    app.add_account('second')
    app.mw.show_account()
    app.add_entry(date='03/01/2009', description='transfer', transfer='first', increase='42')
    export_filename = unicode(tmppath + 'export.qif')
    app.doc.save_to_qif(export_filename)
    exported = open(export_filename).read()
    reference = open(TestData.filepath('qif', 'export_ref_transfer.qif')).read()
    eq_(exported, reference)
