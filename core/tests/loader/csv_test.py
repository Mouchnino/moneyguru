# Created By: Virgil Dupras
# Created On: 2009-01-18
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from pytest import raises
from hscommon.testutil import eq_
from hscommon.currency import USD, EUR

from ...exception import FileFormatError
from ...loader.csv import Loader, CsvField
from ...model.amount import Amount
from ..base import testdata

def test_fortis():
    # a fortis csv import. ';' delimiter, with headers.
    loader = Loader(USD)
    loader.parse(testdata.filepath('csv/fortis.csv'))
    # there are blank lines, but they have been stripped out
    eq_(len(loader.lines), 19)
    eq_(len(loader.lines[0]), 8)
    # the lines below until the load() are the equivalent of the user linking columns with fields
    # and removing the first line.
    loader.columns = [CsvField.Reference, CsvField.Date, None, CsvField.Amount, CsvField.Currency,
        CsvField.Description]
    loader.lines = loader.lines[1:]
    loader.load()
    eq_(len(loader.accounts), 1)
    [account] = loader.accounts
    eq_(account.name, 'CSV Import')
    transactions = loader.transactions
    eq_(len(transactions), 18)
    txn = transactions[0]
    eq_(txn.date, date(2008, 12, 1))
    eq_(txn.description, 'RETRAIT A UN DISTRIBUTEUR FORTIS')
    eq_(txn.splits[0].account.name, 'CSV Import')
    eq_(txn.splits[0].amount, Amount(-100, EUR))
    assert txn.splits[1].account is None
    eq_(txn.splits[1].amount, Amount(100, EUR))
    eq_(txn.splits[0].reference, '2008-0069')

def test_fortis_with_r_linesep():
    # Same as fortis.csv, but instead of being \r\n lineseps, it's \r only
    loader = Loader(USD)
    loader.parse(testdata.filepath('csv/fortis_with_r_linesep.csv'))
    eq_(len(loader.lines), 19) # no crash

def test_mixed_linesep():
    # A file with the header line ending with \r\n, but the rest of the lines ending with \n
    # this used to mix moneyGuru up and it wouldn't have the correct field sep (it would use
    # the comma from the amounts). This is really a weird case, for which I couldn't figure
    # the exact cause (it's somewhere in the sniffer). Oh, and watch out if you edit the csv
    # because the linesep will likely be made uniform by the editor (I used a hex editor to 
    # create this one).
    loader = Loader(USD)
    loader.parse(testdata.filepath('csv/mixed_linesep.csv'))
    eq_(len(loader.lines[0]), 3) # The correct fieldsep is found, thus all the fields are there.

def test_lots_of_noise():
    # this file has 4 lines of non-separated header (Sniffer doesn't work) and a footer.
    # The number of column must be according to the *data* columns
    loader = Loader(USD)
    loader.parse(testdata.filepath('csv/lots_of_noise.csv'))
    assert all(len(line) == 6 for line in loader.lines)

def test_no_transactions():
    # a Deutsch Bank export without transactions in it. It would raise an error during sniffing
    loader = Loader(USD)
    with raises(FileFormatError):
        loader.parse(testdata.filepath('csv/no_transaction.csv'))

def test_unquoted_with_footer():
    # It seems that the sniffer has problems with regular csv files that end with a non-data
    # footer. This is strange, since the "lots_of_noise" file has way more "noise" than this
    # file and the sniffer still gets it correctly.
    loader = Loader(USD)
    loader.parse(testdata.filepath('csv/unquoted_with_footer.csv'))
    eq_(len(loader.lines), 3) # no crash

def test_with_comments():
    # the 'comments.csv' file has lines starting with '#' which the parser had problems with.
    loader = Loader(USD)
    loader.parse(testdata.filepath('csv/comments.csv')) # no exception
    # It's not because the commented lines weren't passed to the sniffer that they don't show
    # up in the csv options panel. All lines must be there.
    eq_(len(loader.lines), 6)

def test_null_character():
    # Purge the csv file from null characters before sending it to the csv loader so that we avoid
    # crashes.
    loader = Loader(USD)
    loader.parse(testdata.filepath('csv/null_character.csv')) # no exception
    eq_(len(loader.lines), 4)
