# Created By: Virgil Dupras
# Created On: 2008-07-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base import DocumentGUIObject

class SearchField(DocumentGUIObject):
    @property
    def query(self):
        return self.document.filter_string
    
    @query.setter
    def query(self, value):
        self.document.filter_string = value
    
    #--- Events
    def filter_applied(self):
        self.view.refresh()
    

    