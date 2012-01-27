# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtGui import QWidget

class BaseView(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)
        self.model = model
        self._setup()
        # self.model.view usually triggers calls that require the view's children to be set up.
        self.model.view = self
    
    def _setup(self):
        raise NotImplementedError()
    
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fit(self, 42, 42, expandH=True, expandV=True)
    
