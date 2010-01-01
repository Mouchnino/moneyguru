# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QWidget

class BaseView(QWidget):
    PRINT_TITLE_FORMAT = "Some Title {startDate} - {endDate}"
    
    def __init__(self):
        QWidget.__init__(self, None)
        self.children = []
    
    def connect(self):
        for child in self.children:
            child.model.connect()
    
    def disconnect(self):
        for child in self.children:
            child.model.disconnect()
    
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fit(self, 42, 42, expandH=True, expandV=True)
    
