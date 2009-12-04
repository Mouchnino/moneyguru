# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QWidget

from support.view_printer import ViewPrinter

class BaseView(QWidget):
    def __init__(self):
        QWidget.__init__(self, None)
        self.children = []
    
    def connect(self):
        for child in self.children:
            child.model.connect()
    
    def disconnect(self):
        for child in self.children:
            child.model.disconnect()
    
    def print_(self, printer, painter):
        viewPrinter = ViewPrinter(printer, painter)
        viewPrinter.fit(self, QSize(42, 42), expandH=True, expandV=True)
        viewPrinter.render()
    
