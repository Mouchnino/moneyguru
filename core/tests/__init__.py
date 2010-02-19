# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-19
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import xmlrpclib

from hsutil.patcher import Patcher

from ..model.currency import RatesDB
from ..model import currency as currency_module

def setup_package():
    global patcher
    patcher = Patcher()
    # The vast majority of moneyGuru's tests require that ensure_rates is patched to nothing to
    # avoid hitting the currency server during tests. However, some tests still need it. This is
    # why we keep it around so that those tests can re-patch it.
    global original_rates_db_ensure_rates
    original_rates_db_ensure_rates = RatesDB.ensure_rates
    patcher.patch(RatesDB, 'ensure_rates', lambda *a, **kw: None)
    currency_module.initialize_db(':memory:')
    def raise_if_called(*args, **kwargs):
        raise Exception('This is not supposed to be used in a test case')
    patcher.patch(xmlrpclib, 'ServerProxy', raise_if_called)

def teardown_package():
    global patcher
    patcher.unpatch()

def get_original_rates_db_ensure_rates():
    global original_rates_db_ensure_rates
    return original_rates_db_ensure_rates
