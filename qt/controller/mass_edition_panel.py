# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.currency import Currency

from .panel import Panel
from ..ui.mass_edition_panel_ui import Ui_MassEditionPanel

class MassEditionPanel(Panel, Ui_MassEditionPanel):
    FIELDS = [
        ('dateCheckBox', 'date_enabled'),
        ('descriptionCheckBox', 'description_enabled'),
        ('payeeCheckBox', 'payee_enabled'),
        ('checknoCheckBox', 'checkno_enabled'),
        ('fromCheckBox', 'from_enabled'),
        ('toCheckBox', 'to_enabled'),
        ('amountCheckBox', 'amount_enabled'),
        ('currencyCheckBox', 'currency_enabled'),
        ('dateEdit', 'date'),
        ('descriptionEdit', 'description'),
        ('payeeEdit', 'payee'),
        ('checknoEdit', 'checkno'),
        ('fromEdit', 'from_'),
        ('toEdit', 'to'),
        ('amountEdit', 'amount'),
        ('currencyComboBox', 'currency_index'),
    ]
    
    def __init__(self, mainwindow):
        Panel.__init__(self, mainwindow)
        self.mainwindow = mainwindow
        self._setupUi()
        self.model = mainwindow.model.mass_edit_panel
        self.model.view = self
    
    def _setupUi(self):
        self.setupUi(self)
        availableCurrencies = ['{currency.code} - {currency.name}'.format(currency=currency) for currency in Currency.all]
        self.currencyComboBox.addItems(availableCurrencies)
    
    def _loadFields(self):
        Panel._loadFields(self)
        disableableWidgets = [self.fromCheckBox, self.fromEdit, self.toCheckBox, self.toEdit]
        for widget in disableableWidgets:
            self.fromCheckBox.setEnabled(self.model.can_change_accounts)
        disableableWidgets = [self.amountCheckBox, self.amountEdit]
        for widget in disableableWidgets:
            self.fromCheckBox.setEnabled(self.model.can_change_amount)
    
    #--- model --> view
    def refresh(self):
        # We have to refresh the checkboxes' state.
        self._loadFields()
    
