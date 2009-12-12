# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-10
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.currency import Currency

from moneyguru.gui.account_panel import AccountPanel as AccountPanelModel

from .panel import Panel
from ui.account_panel_ui import Ui_AccountPanel

class AccountPanel(Panel, Ui_AccountPanel):
    FIELDS = [
        ('nameEdit', 'name'),
        ('typeComboBox', 'type_index'),
        ('currencyComboBox', 'currency_index'),
    ]
    
    def __init__(self, parent, doc):
        Panel.__init__(self, parent)
        self._setupUi()
        self.doc = doc
        self.model = AccountPanelModel(view=self, document=doc.model)
    
    def _setupUi(self):
        self.setupUi(self)
        availableCurrencies = ['{currency.code} - {currency.name}'.format(currency=currency) for currency in Currency.all]
        self.currencyComboBox.addItems(availableCurrencies)
    
