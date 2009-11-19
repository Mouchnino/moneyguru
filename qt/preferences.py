# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-17
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from qtlib.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    def _load_values(self, settings, get):
        self.registration_code = get('RegistrationCode', self.registration_code)
        self.registration_email = get('RegistrationEmail', self.registration_email)
        self.netWorthExpandedPaths = get('NetWorthExpandedPaths', self.netWorthExpandedPaths)
        self.profitLossExpandedPaths = get('ProfitLossExpandedPaths', self.profitLossExpandedPaths)
    
    def reset(self):
        self.registration_code = ''
        self.registration_email = ''
        self.netWorthExpandedPaths = [[0], [1]] # Asset and Liability nodes
        self.profitLossExpandedPaths = [[0], [1]] # Income and Expense nodes
    
    def _save_values(self, settings, set_):
        set_('RegistrationCode', self.registration_code)
        set_('RegistrationEmail', self.registration_email)
        set_('NetWorthExpandedPaths', self.netWorthExpandedPaths)
        set_('ProfitLossExpandedPaths', self.profitLossExpandedPaths)
    
