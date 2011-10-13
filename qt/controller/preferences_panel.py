# Created By: Virgil Dupras
# Created On: 2009-11-28
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import (QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QComboBox, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox, QSizePolicy, QSpacerItem)

from hscommon.currency import Currency
from hscommon.trans import tr as trbase
from core.model.date import clean_format

tr = lambda s: trbase(s, "PreferencesPanel")

SUPPORTED_LANGUAGES = ['en', 'fr', 'de', 'it', 'cs']
LANG2NAME = {
    'en': tr('English'),
    'fr': tr('French'),
    'de': tr('German'),
    'it': tr('Italian'),
    'cs': tr('Czech'),
}

class PreferencesPanel(QDialog):
    def __init__(self, parent, app):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, parent, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.app = app
        self._setupUi()
        
        self.dateFormatEdit.editingFinished.connect(self.dateFormatEdited)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Preferences"))
        self.resize(332, 253)
        self.verticalLayout = QVBoxLayout(self)
        self.formLayout = QFormLayout()
        
        self.horizontalLayout = QHBoxLayout()
        self.autoSaveIntervalSpinBox = QSpinBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.autoSaveIntervalSpinBox.sizePolicy().hasHeightForWidth())
        self.autoSaveIntervalSpinBox.setSizePolicy(sizePolicy)
        self.horizontalLayout.addWidget(self.autoSaveIntervalSpinBox)
        self.label_5 = QLabel(tr("minute(s) (0 for none)"), self)
        self.horizontalLayout.addWidget(self.label_5)
        self.formLayout.addRow(tr("Auto-save interval:"), self.horizontalLayout)
        
        self.dateFormatEdit = QLineEdit(self)
        self.dateFormatEdit.setMaximumSize(QSize(140, 0xffffff))
        self.formLayout.addRow(tr("Date Format:"), self.dateFormatEdit)
        
        self.nativeCurrencyComboBox = QComboBox(self)
        availableCurrencies = ['{currency.code} - {currency.name}'.format(currency=currency) for currency in Currency.all]
        self.nativeCurrencyComboBox.addItems(availableCurrencies)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nativeCurrencyComboBox.sizePolicy().hasHeightForWidth())
        self.nativeCurrencyComboBox.setSizePolicy(sizePolicy)
        self.nativeCurrencyComboBox.setEditable(True)
        self.formLayout.addRow(tr("Native Currency:"), self.nativeCurrencyComboBox)
        
        self.languageComboBox = QComboBox(self)
        for lang in SUPPORTED_LANGUAGES:
            self.languageComboBox.addItem(LANG2NAME[lang])
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.languageComboBox.sizePolicy().hasHeightForWidth())
        self.languageComboBox.setSizePolicy(sizePolicy)
        self.formLayout.addRow(tr("Language:"), self.languageComboBox)
        self.verticalLayout.addLayout(self.formLayout)
        
        self.scopeDialogCheckBox = QCheckBox(tr("Show scope dialog when modifying a scheduled transaction"), self)
        self.verticalLayout.addWidget(self.scopeDialogCheckBox)
        self.autoDecimalPlaceCheckBox = QCheckBox(tr("Automatically place decimals when typing"), self)
        self.verticalLayout.addWidget(self.autoDecimalPlaceCheckBox)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
    
    def load(self):
        appm = self.app.model
        self.autoSaveIntervalSpinBox.setValue(appm.autosave_interval)
        self.dateFormatEdit.setText(self.app.prefs.dateFormat)
        self.nativeCurrencyComboBox.setCurrentIndex(Currency.all.index(appm.default_currency))
        self.scopeDialogCheckBox.setChecked(self.app.prefs.showScheduleScopeDialog)
        self.autoDecimalPlaceCheckBox.setChecked(appm.auto_decimal_place)
        try:
            langindex = SUPPORTED_LANGUAGES.index(self.app.prefs.language)
        except ValueError:
            langindex = 0
        self.languageComboBox.setCurrentIndex(langindex)
    
    def save(self):
        restartRequired = False
        appm = self.app.model
        appm.autosave_interval = self.autoSaveIntervalSpinBox.value()
        if self.dateFormatEdit.text() != self.app.prefs.dateFormat:
            restartRequired = True
        self.app.prefs.dateFormat = self.dateFormatEdit.text()
        if self.nativeCurrencyComboBox.currentIndex() >= 0:
            appm.default_currency = Currency.all[self.nativeCurrencyComboBox.currentIndex()]
        self.app.prefs.showScheduleScopeDialog = self.scopeDialogCheckBox.isChecked()
        appm.auto_decimal_place = self.autoDecimalPlaceCheckBox.isChecked()
        lang = SUPPORTED_LANGUAGES[self.languageComboBox.currentIndex()]
        oldlang = self.app.prefs.language
        if oldlang not in SUPPORTED_LANGUAGES:
            oldlang = 'en'
        if lang != oldlang:
            restartRequired = True
        self.app.prefs.language = lang
        if restartRequired:
            QMessageBox.information(self, "", tr("moneyGuru has to restart for these changes to take effect"))
    
    #--- Signals
    def dateFormatEdited(self):
        self.dateFormatEdit.setText(clean_format(self.dateFormatEdit.text()))
    

if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication, QDialog
    app = QApplication([])
    dialog = QDialog(None)
    PreferencesPanel._setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())