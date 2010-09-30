# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QMessageBox

from hscommon.currency import Currency
from core.trans import tr

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
        self.yearStartComboBox.setCurrentIndex(appm.year_start_month - 1)
        self.autoSaveIntervalSpinBox.setValue(appm.autosave_interval)
        self.nativeCurrencyComboBox.setCurrentIndex(Currency.all.index(appm.default_currency))
        self.scopeDialogCheckBox.setChecked(self.app.prefs.showScheduleScopeDialog)
        self.autoDecimalPlaceCheckBox.setChecked(appm.auto_decimal_place)
        langindex = {'fr': 1, 'de': 2}.get(self.app.prefs.language, 0)
        self.languageComboBox.setCurrentIndex(langindex)
    
    def save(self):
        appm = self.app.model
        appm.first_weekday = self.firstWeekdayComboBox.currentIndex()
        appm.ahead_months = self.aheadMonthsSpinBox.value()
        appm.year_start_month = self.yearStartComboBox.currentIndex() + 1
        appm.autosave_interval = self.autoSaveIntervalSpinBox.value()
        if self.nativeCurrencyComboBox.currentIndex() >= 0:
            appm.default_currency = Currency.all[self.nativeCurrencyComboBox.currentIndex()]
        self.app.prefs.showScheduleScopeDialog = self.scopeDialogCheckBox.isChecked()
        appm.auto_decimal_place = self.autoDecimalPlaceCheckBox.isChecked()
        langs = ['en', 'fr', 'de']
        lang = langs[self.languageComboBox.currentIndex()]
        oldlang = self.app.prefs.language
        if oldlang not in langs:
            oldlang = 'en'
        if lang != oldlang:
            QMessageBox.information(self, "", tr("moneyGuru has to restart for language changes to take effect"))
        self.app.prefs.language = lang
    
