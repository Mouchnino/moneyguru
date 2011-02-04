# Created By: Virgil Dupras
# Created On: 2010-02-19
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import xmlrpc.client

from hscommon.testutil import Patcher

from ..model.currency import RatesDB
from ..model import currency as currency_module

global patcher
global original_rates_db_ensure_rates
global is_ratesdb_patched
patcher = None
original_rates_db_ensure_rates = RatesDB.ensure_rates
is_ratesdb_patched = False

def setup_package():
    patcher = Patcher()
    # The vast majority of moneyGuru's tests require that ensure_rates is patched to nothing to
    # avoid hitting the currency server during tests. However, some tests still need it. This is
    # why we keep it around so that those tests can re-patch it.
    patcher.patch(RatesDB, 'ensure_rates', lambda self, start_date, currencies: None)
    currency_module.initialize_db(':memory:')
    def raise_if_called(*args, **kwargs):
        raise Exception('This is not supposed to be used in a test case')
    patcher.patch(xmlrpc.client, 'ServerProxy', raise_if_called)
    is_ratesdb_patched = True

def ensure_ratesdb_patched():
    # I've noticed that Nose doesn't seem to call setup_package is nosetests hasn't been called
    # from inside that package (for example, if we call it from moneyGuru's root folder). This is
    # pretty bad because we don't want the currency server to be hit by anyone running this test
    # suite from moneyGuru's root folder. So, what I did is that I call this function every time a
    # TestApp instance is created, just to be sure.
    if not is_ratesdb_patched:
        setup_package()

def teardown_package():
    patcher.unpatch()

def get_original_rates_db_ensure_rates():
    
    return original_rates_db_ensure_rates
