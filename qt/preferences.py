# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-17
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op

from qtlib.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    def _load_values(self, settings, get):
        self.registration_code = get('RegistrationCode', self.registration_code)
        self.registration_email = get('RegistrationEmail', self.registration_email)
        self.recentDocuments = get('RecentDocuments', self.recentDocuments)
        self.recentDocuments = filter(op.exists, self.recentDocuments)
        self.netWorthExpandedPaths = get('NetWorthExpandedPaths', self.netWorthExpandedPaths)
        self.profitLossExpandedPaths = get('ProfitLossExpandedPaths', self.profitLossExpandedPaths)
    
    def reset(self):
        self.registration_code = ''
        self.registration_email = ''
        self.recentDocuments = []
        self.netWorthExpandedPaths = [[0], [1]] # Asset and Liability nodes
        self.profitLossExpandedPaths = [[0], [1]] # Income and Expense nodes
        self.networthSheetChangeColumnVisible = False
        self.networthSheetChangePercColumnVisible = False
        self.networthSheetStartColumnVisible = True
        self.networthSheetBudgetedColumnVisible = True
        self.networthSheetGraphVisible = True
        self.networthSheetPieChartsVisible = True
        self.profitSheetChangeColumnVisible = False
        self.profitSheetChangePercColumnVisible = False
        self.profitSheetLastColumnVisible = True
        self.profitSheetBudgetedColumnVisible = True
        self.profitSheetGraphVisible = True
        self.profitSheetPieChartsVisible = True
        self.transactionTableDescriptionColumnVisible = True
        self.transactionTablePayeeColumnVisible = False
        self.transactionTableChecknoColumnVisible = False
        self.entryTableDescriptionColumnVisible = True
        self.entryTablePayeeColumnVisible = False
        self.entryTableChecknoColumnVisible = False
        self.entryTableGraphVisible = True
        self.scheduleTableDescriptionColumnVisible = True
        self.scheduleTablePayeeColumnVisible = False
        self.scheduleTableChecknoColumnVisible = False
    
    def _save_values(self, settings, set_):
        set_('RegistrationCode', self.registration_code)
        set_('RegistrationEmail', self.registration_email)
        set_('RecentDocuments', self.recentDocuments)
        set_('NetWorthExpandedPaths', self.netWorthExpandedPaths)
        set_('ProfitLossExpandedPaths', self.profitLossExpandedPaths)
    
