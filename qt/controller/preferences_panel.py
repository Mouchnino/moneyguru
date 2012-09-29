# Created By: Virgil Dupras
# Created On: 2009-11-28
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QSize, QSettings
from PyQt4.QtGui import (QDialog, QMessageBox, QVBoxLayout, QFormLayout, QLabel, QComboBox,
    QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox)

from hscommon.trans import trget
from qtlib.preferences import LANGNAMES
from qtlib.util import verticalSpacer, horizontalWrap
from core.model.date import clean_format

tr = trget('ui')

SUPPORTED_LANGUAGES = ['en', 'fr', 'de', 'it', 'cs', 'nl']

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
        self.resize(332, 170)
        self.verticalLayout = QVBoxLayout(self)
        self.formLayout = QFormLayout()
        
        self.autoSaveIntervalSpinBox = QSpinBox(self)
        self.autoSaveIntervalSpinBox.setMaximumSize(QSize(70, 0xffffff))
        self.label_5 = QLabel(tr("minute(s) (0 for none)"), self)
        self.formLayout.addRow(tr("Auto-save interval:"),
            horizontalWrap([self.autoSaveIntervalSpinBox, self.label_5]))
        
        self.dateFormatEdit = QLineEdit(self)
        self.dateFormatEdit.setMaximumSize(QSize(140, 0xffffff))
        self.formLayout.addRow(tr("Date format:"), self.dateFormatEdit)

        self.fontSizeSpinBox = QSpinBox()
        self.fontSizeSpinBox.setMinimum(5)
        self.fontSizeSpinBox.setMaximumSize(QSize(70, 0xffffff))
        self.formLayout.addRow(tr("Font size:"), self.fontSizeSpinBox)
        
        self.languageComboBox = QComboBox(self)
        for lang in SUPPORTED_LANGUAGES:
            self.languageComboBox.addItem(LANGNAMES[lang])
        self.languageComboBox.setMaximumSize(QSize(140, 0xffffff))
        self.formLayout.addRow(tr("Language:"), self.languageComboBox)
        self.verticalLayout.addLayout(self.formLayout)
        
        self.scopeDialogCheckBox = QCheckBox(tr("Show scope dialog when modifying a scheduled transaction"), self)
        self.verticalLayout.addWidget(self.scopeDialogCheckBox)
        self.autoDecimalPlaceCheckBox = QCheckBox(tr("Automatically place decimals when typing"), self)
        self.verticalLayout.addWidget(self.autoDecimalPlaceCheckBox)
        self.debugModeCheckBox = QCheckBox(tr("Debug mode (restart required)"), self)
        self.verticalLayout.addWidget(self.debugModeCheckBox)
        self.verticalLayout.addItem(verticalSpacer())
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
    
    def load(self):
        appm = self.app.model
        self.autoSaveIntervalSpinBox.setValue(appm.autosave_interval)
        self.dateFormatEdit.setText(self.app.prefs.dateFormat)
        self.fontSizeSpinBox.setValue(self.app.prefs.tableFontSize)
        self.scopeDialogCheckBox.setChecked(appm.show_schedule_scope_dialog)
        self.autoDecimalPlaceCheckBox.setChecked(appm.auto_decimal_place)
        self.debugModeCheckBox.setChecked(bool(QSettings().value('DebugMode')))
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
        self.app.prefs.tableFontSize = self.fontSizeSpinBox.value()
        appm.show_schedule_scope_dialog = self.scopeDialogCheckBox.isChecked()
        appm.auto_decimal_place = self.autoDecimalPlaceCheckBox.isChecked()
        QSettings().setValue('DebugMode', self.debugModeCheckBox.isChecked())
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