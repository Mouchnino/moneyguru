# Created By: Virgil Dupras
# Created On: 2010-10-26
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hsutil.testutil import eq_
from hscommon.currency import USD

from ..gui.export_panel import ExportFormat
from ..loader.csv import Loader as CSVLoader
from .base import TestApp, with_app

#--- Utils
def export_to_csv(app):
    filepath = str(app.tmppath() + 'foo.csv')
    app.mw.export()
    app.expanel.export_format = ExportFormat.CSV
    app.expanel.export_path = filepath
    app.expanel.save()
    return filepath

#---
def app_transaction_with_payee_and_checkno():
    app = TestApp()
    app.add_account('Checking')
    app.add_txn('10/10/2007', 'Deposit', payee='Payee', from_='Salary', to='Checking',
        amount='42.00', checkno='42')
    return app

@with_app(app_transaction_with_payee_and_checkno)
def test_export_simple_txn_to_csv(app):
    expath = export_to_csv(app)
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
    expath = export_to_csv(app)
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
    expath = export_to_csv(app) # don't crash
    loader = CSVLoader(USD)
    loader.parse(expath)
    lines = [l for l in loader.lines if l]
    eq_(len(lines), 2)
