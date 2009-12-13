# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import tempfile

from PyQt4.QtCore import pyqtSignal, Qt, QObject, QFile
from PyQt4.QtGui import QFileDialog, QMessageBox, QApplication

from moneyguru.document import Document as DocumentModel

from controller.reconciliation_warning_dialog import ReconciliationWarningDialog
from controller.schedule_scope_dialog import ScheduleScopeDialog

class Document(QObject):
    def __init__(self, app):
        QObject.__init__(self)
        self.app = app
        self.documentPath = None
        self.model = DocumentModel(view=self, app=app.model)
    
    def _save(self, docpath):
        if not self.app.model.registered and len(self.model.transactions) > 100:
            msg = "You have reached the limits of this demo version. You must buy moneyGuru to save the document."
            QMessageBox.warning(self.app.mainWindow, "Registration Required", msg)
            return False
        self.model.save_to_xml(docpath)
        return True
    
    #--- Public
    def close(self):
        if self.documentPath:
            self.model.close()
    
    def confirmDestructiveAction(self):
        # Asks whether the user wants to continue before continuing with an action that will replace
        # the current document. Will save the document as needed. Returns True if the action can
        # continue.
        if not self.model.is_dirty():
            return True
        title = "Unsaved Document"
        msg = "Do you want to save your changes before continuing?"
        buttons = QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard
        result = QMessageBox.question(self.app.mainWindow, title, msg, buttons)
        if result == QMessageBox.Save:
            self.doc.save()
            if self.doc.model.is_dirty(): # "save as" was cancelled
                return False
            else:
                return True
        elif result == QMessageBox.Cancel:
            return False
        elif result == QMessageBox.Discard:
            return True
    
    def exportToQIF(self):
        title = "Export to QIF"
        filters = "QIF Files (*.qif)"
        docpath = unicode(QFileDialog.getSaveFileName(self.app.mainWindow, title, 'export.qif', '', filters))
        if docpath:
            self.doc.model.save_to_qif(docpath)
    
    def importDocument(self):
        title = "Select a document to import"
        filters = "Supported files (*.moneyguru *.ofx *.qfx *.qif *.csv *.txt)"
        docpath = unicode(QFileDialog.getOpenFileName(self.app.mainWindow, title, '', filters))
        if docpath:
            self.model.parse_file_for_import(docpath)
    
    def new(self):
        if not self.confirmDestructiveAction():
            return
        self.close()
        self.model.clear()
    
    def open(self, docpath):
        if not self.confirmDestructiveAction():
            return
        self.close()
        self.model.load_from_xml(docpath)
        self.documentPath = docpath
        self.documentOpened.emit(docpath)
    
    def openDocument(self):
        title = "Select a document to load"
        filters = "moneyGuru Documents (*.moneyguru)"
        docpath = unicode(QFileDialog.getOpenFileName(self.app.mainWindow, title, '', filters))
        if docpath:
            self.open(docpath)
    
    def openExampleDocument(self):
        if not self.confirmDestructiveAction():
            return
        self.close()
        dirpath = tempfile.mkdtemp()
        destpath = op.join(dirpath, 'example.moneyguru')
        QFile.copy(':/example.moneyguru', destpath)
        self.model.load_from_xml(destpath)
        self.model.adjust_example_file()
        self.documentPath = None # As if it was a new doc. Save As is required.
    
    def save(self):
        if self.documentPath is not None:
            self._save(self.documentPath)
        else:
            self.saveAs()
    
    def saveAs(self):
        title = "Save As"
        filters = "moneyGuru Documents (*.moneyguru)"
        docpath = unicode(QFileDialog.getSaveFileName(self.app.mainWindow, title, '', filters))
        if docpath:
            if self._save(docpath):
                self.documentPath = docpath
                self.documentSavedAs.emit(docpath)
    
    # model --> view
    def confirm_unreconciliation(self, affectedSplitCount):
        dialog = ReconciliationWarningDialog(affectedSplitCount, self.app.mainWindow)
        return dialog.askForResolution()
    
    def query_for_schedule_scope(self):
        if QApplication.keyboardModifiers() & Qt.ShiftModifier:
            return True
        if not self.app.prefs.showScheduleScopeDialog:
            return False
        dialog = ScheduleScopeDialog(self.app.mainWindow)
        return dialog.exec_() == ScheduleScopeDialog.Accepted
    
    #--- Signals
    documentOpened = pyqtSignal(unicode)
    documentSavedAs = pyqtSignal(unicode)
