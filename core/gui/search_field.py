# Created By: Virgil Dupras
# Created On: 2008-07-21
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .base import DocumentGUIObject

class SearchField(DocumentGUIObject):
    def __init__(self, view, mainwindow):
        DocumentGUIObject.__init__(self, view, mainwindow.document)
    
    @property
    def query(self):
        return self.document.filter_string
    
    @query.setter
    def query(self, value):
        self.document.filter_string = value
    
    #--- Events
    def filter_applied(self):
        self.view.refresh()
    

    