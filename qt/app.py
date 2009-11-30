# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import pyqtSignal, SIGNAL, QCoreApplication
from PyQt4.QtGui import QDialog

from qtlib.about_box import AboutBox
from qtlib.app import Application as ApplicationBase
from qtlib.reg import Registration

from moneyguru.app import Application as MoneyGuruModel

from controller.document import Document
from controller.main_window import MainWindow
from controller.csv_options import CSVOptionsWindow
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
        self.model = MoneyGuruModel(view=self)
        # on the Qt side, we're single document based, so it's one doc per app.
        self.doc = Document(app=self)
        self.doc.model.connect()
        self.mainWindow = MainWindow(doc=self.doc)
        self.csvOptionsWindow = CSVOptionsWindow(doc=self.doc)
        self.csvOptionsWindow.model.connect()
        self.preferencesPanel = PreferencesPanel(app=self)
        self.viewOptions = ViewOptionsDialog(app=self)
        self.aboutBox = AboutBox(self.mainWindow, self)
        self.reg = Registration(self.model)
        self.model.set_registration(self.prefs.registration_code, self.prefs.registration_email)
        self.mainWindow.updateOptionalWidgetsVisibility()
        if self.prefs.recentDocuments:
            self.doc.open(self.prefs.recentDocuments[0])
        
        self.connect(self, SIGNAL('applicationFinishedLaunching()'), self.applicationFinishedLaunching)
        QCoreApplication.instance().aboutToQuit.connect(self.applicationWillTerminate)
    
    #--- Public
    def askForRegCode(self):
        self.reg.ask_for_code()
    
    def showAboutBox(self):
        self.aboutBox.show()
    
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
        self.mainWindow.show()
    
    def applicationWillTerminate(self):
        self.doc.close()
        self.willSavePrefs.emit()
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
    
