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
    
    def restoreSubviewsSize(self):
        # This is called by the main window just after the base view has been added to the widget
        # stack. This means that its size has just been adjusted and now is the time to restore,
        # if needed, the sizes of the subviews. It is also called by the model callback
        # restore_subviews_size() which happens when a document is loaded.
        pass
    
    #--- model --> view
    def restore_subviews_size(self):
        self.restoreSubviewsSize()
