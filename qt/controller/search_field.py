# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-20
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import QObject

from core.gui.search_field import SearchField as SearchFieldModel

class SearchField(QObject):
    def __init__(self, mainwindow, view):
        QObject.__init__(self)
        self.view = view
        self.model = SearchFieldModel(mainwindow=mainwindow.model, view=self)
        
        self.view.searchChanged.connect(self.searchChanged)
    
    #--- Event Handling
    def searchChanged(self):
        self.model.query = unicode(self.view.text())
    
    #--- model --> view
    def refresh(self):
        self.view.setText(self.model.query)
    