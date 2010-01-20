# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os.path as op

from PyQt4.QtCore import pyqtSignal, SIGNAL, QCoreApplication, QLocale, QString, QUrl
from PyQt4.QtGui import QDialog, QDesktopServices

from hsutil.currency import Currency

from qtlib.about_box import AboutBox
from qtlib.app import Application as ApplicationBase
from qtlib.reg import Registration

from core.app import Application as MoneyGuruModel

from controller.document import Document
from controller.main_window import MainWindow
from controller.import_.window import ImportWindow
from controller.import_.csv_options import CSVOptionsWindow
from controller.preferences_panel import PreferencesPanel
from controller.view_options import ViewOptionsDialog
from preferences import Preferences

class MoneyGuru(ApplicationBase):
    VERSION = MoneyGuruModel.VERSION
    LOGO_NAME = 'logo'
    
    def __init__(self):
        ApplicationBase.__init__(self)
        self.prefs = Preferences()
        self.prefs.load()
        locale = QLocale.system()
        dateFormat = unicode(locale.dateFormat(QLocale.ShortFormat))
        decimalSep = unicode(QString(locale.decimalPoint()))
        groupingSep = unicode(QString(locale.groupSeparator()))
        try:
            defaultCurrency = Currency(self.prefs.nativeCurrency)
        except ValueError:
            defaultCurrency = Currency('USD')
        cachePath = unicode(QDesktopServices.storageLocation(QDesktopServices.CacheLocation))
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
        self.viewOptions = ViewOptionsDialog(self.mainWindow, app=self)
        self.aboutBox = AboutBox(self.mainWindow, self)
        self.reg = Registration(self.model)
        self.model.set_registration(self.prefs.registration_code, self.prefs.registration_email)
        self.mainWindow.updateOptionalWidgetsVisibility()
        if sys.argv[1:] and op.exists(sys.argv[1]):
            self.doc.open(sys.argv[1])
        elif self.prefs.recentDocuments:
            self.doc.open(self.prefs.recentDocuments[0])
        
        self.connect(self, SIGNAL('applicationFinishedLaunching()'), self.applicationFinishedLaunching)
        QCoreApplication.instance().aboutToQuit.connect(self.applicationWillTerminate)
    
    #--- Public
    def askForRegCode(self):
        self.reg.ask_for_code()
    
    def showAboutBox(self):
        self.aboutBox.show()
    
    def showHelp(self):
        url = QUrl.fromLocalFile(op.abspath('help/intro.htm'))
        QDesktopServices.openUrl(url)
    
    def showPreferences(self):
        self.preferencesPanel.load()
        if self.preferencesPanel.exec_() == QDialog.Accepted:
            self.preferencesPanel.save()    
    
    def showViewOptions(self):
        self.viewOptions.loadFromPrefs()
        if self.viewOptions.exec_() == QDialog.Accepted:
            self.viewOptions.saveToPrefs()
            self.mainWindow.updateOptionalWidgetsVisibility()
    
    #--- Event Handling
    def applicationFinishedLaunching(self):
        if not self.model.registered:
            self.reg.show_nag()
        if self.prefs.mainWindowIsMaximized:
            self.mainWindow.showMaximized()
        else:
            self.mainWindow.show()
    
    def applicationWillTerminate(self):
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
    
    def setup_as_registered(self):
        self.prefs.registration_code = self.model.registration_code
        self.prefs.registration_email = self.model.registration_email
        self.mainWindow.actionRegister.setVisible(False)
        self.aboutBox.registerButton.hide()
        self.aboutBox.registeredEmailLabel.setText(self.prefs.registration_email)
    
