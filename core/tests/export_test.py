# Created By: Virgil Dupras
# Created On: 2010-10-26
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_
from hscommon.currency import USD

from ..gui.export_panel import ExportFormat
from ..loader.csv import Loader as CSVLoader
from ..loader.qif import Loader as QIFLoader
from .base import TestApp, with_app

#--- Utils
def perform_export(app, options=None):
    filepath = str(app.tmppath() + 'foo.csv')
    app.mw.export()
    app.expanel.export_format = ExportFormat.CSV
    app.expanel.export_path = filepath
    if options is not None:
        for key, value in options.items():
            setattr(app.expanel, key, value)
    app.expanel.save()
    return filepath

#---
@with_app(TestApp)
def test_export_only_current_date_range(app):
    # when the option to export only current date range is selected, well, we only export txns in
    # the current date range.
    app.add_account('foo')
    app.add_txn('01/01/2010', from_='foo', amount='1')
    app.add_txn('01/01/2011', from_='foo', amount='1') # not in the same date range
    options = {'current_daterange_only': True}
    expath = perform_export(app, options)
    loader = CSVLoader(USD)
    loader.parse(expath)
    lines = [l for l in loader.lines if l]
    eq_(len(lines), 2) # header + 1 line
    # QIF too
    options['export_format'] = ExportFormat.QIF
    expath = perform_export(app, options)
    loader = QIFLoader(USD)
    loader.parse(expath)
    eq_(len(loader.blocks), 2) # 1 account + 1 entry

#---
def app_transaction_with_payee_and_checkno():
    app = TestApp()
    app.add_account('Checking')
    app.add_txn('10/10/2007', 'Deposit', payee='Payee', from_='Salary', to='Checking',
        amount='42.00', checkno='42')
    return app

@with_app(app_transaction_with_payee_and_checkno)
def test_export_simple_txn_to_csv(app):
    expath = perform_export(app)
    loader = CSVLoader(USD)
    loader.parse(expath)
    lines = [l for l in loader.lines if l]
    eq_(len(lines), 2)
    expected = ['Checking', '10/10/2007', 'Deposit', 'Payee', '42', 'Salary', '42.00', 'USD']
    eq_(lines[1], expected)

#---
def app_transaction_with_splits():
    app = TestApp()
    app.add_account('checking')
    splits = [
        ('checking', '', '42', ''),
        ('split1', '', '', '20'),
        ('split2', '', '', '22'),
    ]
    app.add_txn_with_splits(splits, '26/10/2010')
    return app

@with_app(app_transaction_with_splits)
def test_export_txn_with_splits_to_csv(app):
    expath = perform_export(app)
    loader = CSVLoader(USD)
    loader.parse(expath)
    lines = [l for l in loader.lines if l]
    eq_(len(lines), 2)
    expected = ['checking', '26/10/2010', '', '', '', 'split1, split2', '42.00', 'USD']
    eq_(lines[1], expected)

#---
def app_txn_with_null_amount():
    app = TestApp()
    app.add_account('checking')
    app.add_txn(to='checking')
    return app

@with_app(app_txn_with_null_amount)
def test_export_txn_with_null_amount(app):
    # Don't crash on txns with null amounts
    expath = perform_export(app) # don't crash
    loader = CSVLoader(USD)
    loader.parse(expath)
    lines = [l for l in loader.lines if l]
    eq_(len(lines), 2)
