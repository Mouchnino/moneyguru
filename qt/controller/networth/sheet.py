# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.balance_sheet import BalanceSheet as BalanceSheetModel
from ..account_sheet import AccountSheet, AccountSheetDelegate
from ..column import Column

class NetWorthSheetDelegate(AccountSheetDelegate):
    BOLD_ATTRS = set(['end'])
    AMOUNT_ATTRS = set(['end', 'start', 'delta', 'delta_perc', 'budgeted'])

class NetWorthSheet(AccountSheet):
    COLUMNS = [
        Column('name', 'Account', 120),
        Column('end', 'End', 100),
        Column('start', 'Start', 100),
        Column('delta', 'Change', 100),
        Column('delta_perc', 'Change %', 100),
        Column('budgeted', 'Budgeted', 100),
    ]
    EXPANDED_NODE_PREF_NAME = 'netWorthExpandedPaths'
    DELEGATE_CLASS = NetWorthSheetDelegate
    
    def __init__(self, doc, view):
        model = BalanceSheetModel(view=self, document=doc.model)
        AccountSheet.__init__(self, doc, model, view)
    
