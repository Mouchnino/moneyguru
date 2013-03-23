# Created By: Eric Mc Sween
# Created On: 2008-02-11
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from pytest import raises
from hscommon.currency import USD, CAD, EUR
from hscommon.testutil import eq_

from ..base import testdata
from ...exception import FileFormatError
from ...loader import ofx
from ...model.amount import Amount

def test_dont_choke_on_empty_files():
    # The ofx loader doesn't choke on an empty file
    loader = ofx.Loader(USD)
    with raises(FileFormatError):
        loader.parse(testdata.filepath('zerofile'))

def test_format_error():
    loader = ofx.Loader(USD)
    with raises(FileFormatError):
        loader.parse(testdata.filepath('ofx', 'invalid.ofx'))

def test_amounts_in_invalid_currency_account():
    loader = ofx.Loader(USD)
    loader.parse(testdata.filepath('ofx', 'invalid_currency.ofx'))
    loader.load()
    account = loader.accounts.find('815-30219-11111-EOP')
    eq_(len(account.entries), 3)
    entry = account.entries[0]
    eq_(entry.amount, Amount(0.02, USD))

def test_blank_line_ofx_attrs():
    # Just make sure that a ofx file starting with a blank line is correctly loaded
    loader = ofx.Loader(USD)
    loader.parse(testdata.filepath('ofx', 'blank_first_line.ofx'))
    loader.load()
    eq_(len(loader.accounts), 1)
    eq_(len(loader.transactions), 5)

#---
def loader_desjardins():
    loader = ofx.Loader(USD)
    loader.parse(testdata.filepath('ofx', 'desjardins.ofx'))
    loader.load()
    return loader

def test_accounts_desjardins():
    loader = loader_desjardins()
    accounts = [(x.name, x.currency, str(x.balance)) for x in loader.account_infos]
    expected = [('815-30219-12345-EOP', 'CAD', '3925.84'), 
                ('815-30219-54321-ES1', 'CAD', '0.00'),
                ('815-30219-11111-EOP', 'USD', '3046.90'),]
    eq_(accounts, expected)

def test_transactions_usd_account():
    loader = loader_desjardins()
    account = loader.accounts.find('815-30219-11111-EOP')
    eq_(len(account.entries), 3)
    entry = account.entries[0]
    eq_(entry.date, date(2008, 1, 31))
    eq_(entry.description, 'Intérêt sur EOP/')
    eq_(entry.amount, Amount(0.02, USD))
    entry = account.entries[1]
    eq_(entry.date, date(2008, 2, 1))
    eq_(entry.description, 'Dépôt au comptoir/')
    eq_(entry.amount, Amount(5029.50, USD))
    entry = account.entries[2]
    eq_(entry.date, date(2008, 2, 1))
    eq_(entry.description, 'Retrait au comptoir/')
    eq_(entry.amount, Amount(-2665, USD))

def test_reference_desjardins():
    # OFX IDs are stored in the accounts and entries.
    loader = loader_desjardins()
    account = loader.accounts[0]
    eq_(account.reference, '700000100|0389347|815-30219-12345-EOP')
    transaction = loader.transaction_infos[0]
    eq_(transaction.reference, 'Th3DJACES')

#---
def loader_ing():
    loader = ofx.Loader(USD)
    loader.parse(testdata.filepath('ofx', 'ing.qfx'))
    loader.load()
    return loader

def test_accounts_ing():
    loader = loader_ing()
    accounts = [(x.name, x.currency) for x in loader.accounts]
    expected = [('123456', CAD)]
    eq_(accounts, expected)

def test_entries_ing():
    loader = loader_ing()
    account = loader.accounts.find('123456')
    eq_(len(account.entries), 1)
    entry = account.entries[0]
    eq_(entry.date, date(2005, 9, 23))
    eq_(entry.description, 'Dépôt')
    eq_(entry.amount, Amount(100, CAD))

#---
def loader_fortis():
    loader = ofx.Loader(EUR)
    loader.parse(testdata.filepath('ofx', 'fortis.ofx'))
    loader.load()
    return loader

def test_reference_fortis():
    # Fortis ofx files don't have a branch id. The reference should exist even without it.
    loader = loader_fortis()
    account = loader.accounts[0]
    eq_(account.reference, 'FORTIS||001-5587496-84')
    transaction = loader.transaction_infos[0]
    eq_(transaction.reference, '20080026')
