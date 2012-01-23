# Created By: Virgil Dupras
# Created On: 2009-11-20
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QObject

class SearchField(QObject):
    def __init__(self, model, view):
        QObject.__init__(self)
        self.view = view
        self.model = model
        
        self.view.searchChanged.connect(self.searchChanged)
    
    #--- Event Handling
    def searchChanged(self):
        self.model.query = str(self.view.text())
    
    #--- model --> view
    def refresh(self):
        self.view.setText(self.model.query)
    