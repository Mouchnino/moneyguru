# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from hsutil.currency import Currency

from ui.preferences_panel_ui import Ui_PreferencesPanel

class PreferencesPanel(QDialog, Ui_PreferencesPanel):
    def __init__(self, parent, app):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, parent, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.app = app
        self._setupUi()
    
    def _setupUi(self):
        self.setupUi(self)
        availableCurrencies = ['{currency.code} - {currency.name}'.format(currency=currency) for currency in Currency.all]
        self.nativeCurrencyComboBox.addItems(availableCurrencies)
    
    def load(self):
        appm = self.app.model
        self.firstWeekdayComboBox.setCurrentIndex(appm.first_weekday)
        self.aheadMonthsSpinBox.setValue(appm.ahead_months)
        self.yearStartComboBox.setCurrentIndex(appm.year_start_month)
        self.autoSaveIntervalSpinBox.setValue(appm.autosave_interval)
        self.nativeCurrencyComboBox.setCurrentIndex(Currency.all.index(appm.default_currency))
        self.scopeDialogCheckBox.setChecked(self.app.prefs.showScheduleScopeDialog)
        self.autoDecimalPlaceCheckBox.setChecked(appm.auto_decimal_place)
    
    def save(self):
        appm = self.app.model
        appm.first_weekday = self.firstWeekdayComboBox.currentIndex()
        appm.ahead_months = self.aheadMonthsSpinBox.value()
        appm.year_start_month = self.yearStartComboBox.currentIndex()
        appm.autosave_interval = self.autoSaveIntervalSpinBox.value()
        if self.nativeCurrencyComboBox.currentIndex() >= 0:
            appm.default_currency = Currency.all[self.nativeCurrencyComboBox.currentIndex()]
        self.app.prefs.showScheduleScopeDialog = self.scopeDialogCheckBox.isChecked()
        appm.auto_decimal_place = self.autoDecimalPlaceCheckBox.isChecked()
    
