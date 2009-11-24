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
from .account_sheet import AccountSheet

class NetWorthSheet(AccountSheet):
    HEADER = ['Account', 'End', 'Start', 'Change', 'Change %', 'Budgeted']
    ROWATTRS = ['name', 'end', 'start', 'delta', 'delta_perc', 'budgeted']
    EXPANDED_NODE_PREF_NAME = 'netWorthExpandedPaths'
    
    def _getModel(self):
        return BalanceSheetModel(view=self, document=self.doc.model)
    
