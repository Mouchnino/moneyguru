# Created By: Virgil Dupras
# Created On: 2009-11-20
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from qtlib.text_field import TextField

class SearchField(TextField):
    def __init__(self, model, view):
        TextField.__init__(self, model, view)
        self.view.searchChanged.connect(self.editingFinished)
    
