# Created By: Virgil Dupras
# Created On: 2009-11-27
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QTabBar

class FilterBar(QObject):
    BUTTONS = [] # (Title, FilterID)
    
    def __init__(self, model, view):
        # the view is a qtlib.RadioBox
        QObject.__init__(self, None)
        self.model = model
        self.model.view = self
        self.view = view
        self.view.items = [title for title, _ in self.BUTTONS]
        
        self.view.itemSelected.connect(self.itemSelected)
    
    #--- Event Handlers
    def itemSelected(self, index):
        _, filterId = self.BUTTONS[index]
        self.model.filter_type = filterId
    
    #--- model --> view
    def refresh(self):
        for index, (title, filterId) in enumerate(self.BUTTONS):
            if filterId is self.model.filter_type:
                self.view.selected_index = index
                break
    
