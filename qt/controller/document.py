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

from PyQt4.QtCore import pyqtSignal, QObject, QFile
from PyQt4.QtGui import QFileDialog, QMessageBox

from moneyguru.document import Document as DocumentModel

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
    
    def exportToQIF(self):
        title = "Export to QIF"
        docpath = unicode(QFileDialog.getSaveFileName(self.app.mainWindow, title, 'export.qif'))
        if docpath:
            self.doc.model.save_to_qif(docpath)
    
    def importDocument(self):
        title = "Select a document to import"
        docpath = unicode(QFileDialog.getOpenFileName(self.app.mainWindow, title))
        if docpath:
            self.model.parse_file_for_import(docpath)
    
    def new(self):
        self.close()
        self.model.clear()
    
    def open(self, docpath):
        self.close()
        self.model.load_from_xml(docpath)
        self.documentPath = docpath
    
    def openDocument(self):
        title = "Select a document to load"
        docpath = unicode(QFileDialog.getOpenFileName(self.app.mainWindow, title))
        if docpath:
            self.open(docpath)
            self.documentOpened.emit(docpath)
    
    def openExampleDocument(self):
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
        docpath = unicode(QFileDialog.getSaveFileName(self.app.mainWindow, title))
        if docpath:
            if self._save(docpath):
                self.documentPath = docpath
                self.documentSavedAs.emit(docpath)
    
    # model --> view
    def confirm_unreconciliation(self, affectedSplitCount):
        return 2 # continue, don't reconcile
    
    def query_for_schedule_scope(self):
        return False
    
    #--- Signals
    documentOpened = pyqtSignal(unicode)
    documentSavedAs = pyqtSignal(unicode)
