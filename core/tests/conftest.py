# Created By: Virgil Dupras
# Created On: 2010-07-11
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# This unit is required to make tests work with py.test. When running

import py

from hscommon.testutil import pytest_funcarg__app

from ..model.currency import RatesDB, Currency
from ..model import currency as currency_module

global_monkeypatch = None

def pytest_configure(config):
    def fake_initialize_db(path):
        ratesdb = RatesDB(':memory:', async=False)
        # We register no rate provider
        Currency.set_rates_db(ratesdb)
    
    global global_monkeypatch
    monkeypatch = config.pluginmanager.getplugin('monkeypatch')
    global_monkeypatch = monkeypatch.monkeypatch()
    # The vast majority of moneyGuru's tests require that ensure_rates is patched to nothing to
    # avoid hitting the currency server during tests. However, some tests still need it. This is
    # why we keep it around so that those tests can re-patch it.
    global_monkeypatch.setattr(currency_module, 'initialize_db', fake_initialize_db)

def pytest_unconfigure(config):
    global global_monkeypatch
    global_monkeypatch.undo()

def pytest_funcarg__monkeypatch(request):
    monkeyplus = request.getfuncargvalue('monkeyplus')
    return monkeyplus