# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import os.path as op

from PyQt4.QtCore import pyqtSignal, SIGNAL, QCoreApplication, QLocale, QUrl
from PyQt4.QtGui import QDialog, QDesktopServices, QApplication, QMessageBox

from hscommon.currency import Currency

from qtlib.about_box import AboutBox
from qtlib.app import Application as ApplicationBase
from qtlib.reg import Registration

from core.app import Application as MoneyGuruModel

from .controller.document import Document
from .controller.main_window import MainWindow
from .controller.import_.window import ImportWindow
from .controller.import_.csv_options import CSVOptionsWindow
from .controller.preferences_panel import PreferencesPanel
from .support.date_edit import DateEdit
from .preferences import Preferences
from .plat import HELP_PATH

class MoneyGuru(ApplicationBase):
    VERSION = MoneyGuruModel.VERSION
    LOGO_NAME = 'logo'
    
    def __init__(self):
        ApplicationBase.__init__(self)
        self.prefs = Preferences()
        self.prefs.load()
        locale = QLocale.system()
        dateFormat = self.prefs.dateFormat
        decimalSep = str(locale.decimalPoint())
        groupingSep = str(locale.groupSeparator())
        try:
            defaultCurrency = Currency(self.prefs.nativeCurrency)
        except ValueError:
            defaultCurrency = Currency('USD')
        cachePath = str(QDesktopServices.storageLocation(QDesktopServices.CacheLocation))
        DateEdit.DATE_FORMAT = dateFormat
        self.model = MoneyGuruModel(view=self, date_format=dateFormat, decimal_sep=decimalSep,
            grouping_sep=groupingSep, default_currency=defaultCurrency, cache_path=cachePath)
        # on the Qt side, we're single document based, so it's one doc per app.
        self.doc = Document(app=self)
        self.doc.model.connect()
        self.mainWindow = MainWindow(doc=self.doc)
        self.importWindow = ImportWindow(self.mainWindow, doc=self.doc)
        self.importWindow.model.connect()
        self.csvOptionsWindow = CSVOptionsWindow(self.mainWindow, doc=self.doc)
        self.csvOptionsWindow.model.connect()
        self.preferencesPanel = PreferencesPanel(self.mainWindow, app=self)
        self.aboutBox = AboutBox(self.mainWindow, self)
        self.mainWindow.updateOptionalWidgetsVisibility()
        if sys.argv[1:] and op.exists(sys.argv[1]):
            self.doc.open(sys.argv[1])
        elif self.prefs.recentDocuments:
            self.doc.open(self.prefs.recentDocuments[0])
        
        self.connect(self, SIGNAL('applicationFinishedLaunching()'), self.applicationFinishedLaunching)
        QCoreApplication.instance().aboutToQuit.connect(self.applicationWillTerminate)
    
    #--- Public
    def askForRegCode(self):
        reg = Registration(self.model)
        reg.ask_for_code()
    
    def showAboutBox(self):
        self.aboutBox.show()
    
    def showHelp(self):
        url = QUrl.fromLocalFile(op.abspath(op.join(HELP_PATH, 'index.html')))
        QDesktopServices.openUrl(url)
    
    def showPreferences(self):
        self.preferencesPanel.load()
        if self.preferencesPanel.exec_() == QDialog.Accepted:
            self.preferencesPanel.save()    
    
    #--- Event Handling
    def applicationFinishedLaunching(self):
        self.model.initial_registration_setup()
        if self.prefs.mainWindowIsMaximized:
            self.mainWindow.showMaximized()
        else:
            self.mainWindow.show()
    
    def applicationWillTerminate(self):
        # This line stops the autosave timer which sometimes prevent the app from quitting.
        self.model.autosave_interval = 0
        self.doc.close()
        self.willSavePrefs.emit()
        self.prefs.nativeCurrency = self.model.default_currency.code
        self.prefs.save()
    
    #--- Signals
    willSavePrefs = pyqtSignal()
    
    #--- model --> view
    def get_default(self, key):
        return self.prefs.get_value(key)
    
    def set_default(self, key, value):
        self.prefs.set_value(key, value)
    
    def show_fairware_nag(self, prompt):
        reg = Registration(self.model)
        reg.show_fairware_nag(prompt)
    
    def show_demo_nag(self, prompt):
        reg = Registration(self.model)
        reg.show_demo_nag(prompt)
    
    def show_message(self, msg):
        window = QApplication.activeWindow()
        QMessageBox.information(window, '', msg)
    
    def open_url(self, url):
        url = QUrl(url)
        QDesktopServices.openUrl(url)
    
    def setup_as_registered(self):
        self.mainWindow.actionRegister.setVisible(False)
        self.aboutBox.registerButton.hide()
        self.aboutBox.registeredEmailLabel.setText(self.prefs.registration_email)
    
