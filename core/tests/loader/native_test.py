# Created By: Virgil Dupras
# Created On: 2008-02-15
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from io import BytesIO
from datetime import date

from pytest import raises
from hscommon.testutil import eq_
from hscommon.currency import USD, PLN

from ..base import testdata
from ...exception import FileFormatError
from ...loader import native
from ...model.account import AccountType
from ...model.amount import Amount

def pytest_funcarg__loader(request):
    return native.Loader(USD)
    
def test_parse_non_xml(loader):
    content = b'this is not xml content'
    with raises(FileFormatError):
        loader._parse(BytesIO(content))

def test_parse_wrong_root_name(loader):
    content = b'<foobar></foobar>'
    with raises(FileFormatError):
        loader._parse(BytesIO(content))

def test_parse_minimal(loader):
    content = b'<moneyguru-file></moneyguru-file>'
    try:
        loader._parse(BytesIO(content))
    except FileFormatError:
        assert False

def test_wrong_date(loader):
    # these used to raise FileFormatError, but now, we just want to make sure that there is no
    # crash.
    content = b'<moneyguru-file><transaction date="bobsleigh" /></moneyguru-file>'
    loader._parse(BytesIO(content))
    loader.load() # no crash

def test_wrong_mtime(loader):
    # these used to raise FileFormatError, but now, we just want to make sure that there is no
    # crash.
    content = b'<moneyguru-file><transaction date="2008-01-01" mtime="abc" /></moneyguru-file>'
    loader._parse(BytesIO(content))
    loader.load() # no crash

def test_account_and_entry_values(loader):
    # Make sure loaded values are correct.
    loader.parse(testdata.filepath('moneyguru', 'simple.moneyguru'))
    loader.load()
    accounts = loader.accounts
    eq_(len(accounts), 3)
    account = accounts[0]
    eq_(account.name, 'Account 1')
    eq_(account.currency, USD)
    account = accounts[1]
    eq_(account.name, 'Account 2')
    eq_(account.currency, PLN)
    account = accounts[2]
    eq_(account.name, 'foobar')
    eq_(account.currency, USD)
    eq_(account.type, AccountType.Expense)
    transactions = loader.transaction_infos
    eq_(len(transactions), 4)
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
    eq_(split.account.name, 'Account 1')
    eq_(split.amount, Amount(-14, USD))
    
    transaction = transactions[3]
    eq_(transaction.date, date(2008, 2, 19))
    eq_(transaction.description, 'Entry 4')
    eq_(transaction.transfer, None)
    eq_(transaction.mtime, 1203095497)
    split = transaction.splits[0]
    eq_(split.account.name, 'Account 2')
    eq_(split.amount, Amount(-101, PLN))
