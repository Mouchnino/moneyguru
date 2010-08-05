# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-10
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hscommon.currency import Currency

from core.gui.account_panel import AccountPanel as AccountPanelModel

from .panel import Panel
from ui.account_panel_ui import Ui_AccountPanel

class AccountPanel(Panel, Ui_AccountPanel):
    FIELDS = [
        ('nameEdit', 'name'),
        ('typeComboBox', 'type_index'),
        ('currencyComboBox', 'currency_index'),
        ('accountNumberEdit', 'account_number'),
        ('notesEdit', 'notes'),
    ]
    
    def __init__(self, mainwindow):
        Panel.__init__(self, mainwindow)
        self._setupUi()
        self.model = AccountPanelModel(view=self, mainwindow=mainwindow.model)
    
    def _setupUi(self):
        self.setupUi(self)
        availableCurrencies = ['{currency.code} - {currency.name}'.format(currency=currency) for currency in Currency.all]
        self.currencyComboBox.addItems(availableCurrencies)
    
