# Created By: Virgil Dupras
# Created On: 2010-10-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hsutil.testutil import eq_

from ...model.account import AccountType
from ..base import TestApp, with_app

#---
@with_app(TestApp)
def test_account_table_order(app):
    app.add_account('d', account_type=AccountType.Asset)
    app.add_account('c', account_type=AccountType.Liability)
    app.add_account('b', account_type=AccountType.Income)
    app.add_account('a', account_type=AccountType.Expense)
    app.mw.export()
    t = app.expanel.table
    eq_(len(t), 4)
    eq_(t[0].name, 'd')
    eq_(t[1].name, 'c')
    eq_(t[2].name, 'b')
    eq_(t[3].name, 'a')

@with_app(TestApp)
def test_default_values(app):
    app.add_account('foo')
    app.mw.export()
    assert app.expanel.export_all
    assert not app.expanel.table[0].export
    assert app.expanel.export_path is None

@with_app(TestApp)
def test_export_only_one_account(app):
    app.add_accounts('foobar', 'foobaz')
    app.mw.export()
    app.expanel.export_all = False
    app.expanel.table[0].export = True
    expath = str(app.tmppath() + 'foo.qif')
    app.expanel.export_path = expath
    app.expanel.save()
    contents = open(expath, 'rt', encoding='utf-8').read()
    assert 'foobaz' not in contents
