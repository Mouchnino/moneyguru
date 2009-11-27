# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-27
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QTabBar

class FilterBar(QObject):
    BUTTONS = [] # (Title, FilterID)
    
    def __init__(self, model, view):
        QObject.__init__(self, None)
        self.model = model
        self.view = view
        for title, filterId in self.BUTTONS:
            self.view.addTab(title)
        
        self.view.currentChanged.connect(self.currentTabChanged)
    
    #--- Event Handlers
    def currentTabChanged(self):
        _, filterId = self.BUTTONS[self.view.currentIndex()]
        self.model.filter_type = filterId
    
    #--- model --> view
    def refresh(self):
        for index, (title, filterId) in enumerate(self.BUTTONS):
            if filterId is self.model.filter_type:
                self.view.setCurrentIndex(index)
                break
    
