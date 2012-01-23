# Created By: Virgil Dupras
# Created On: 2008-07-21
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.base import NoopGUI

class SearchField:
    def __init__(self, mainwindow, view=None):
        self.mainwindow = mainwindow
        self.document = mainwindow.document
        if view is None:
            view = NoopGUI()
        self.view = view
    
    @property
    def query(self):
        return self.document.filter_string
    
    @query.setter
    def query(self, value):
        self.document.filter_string = value
    
    def refresh(self):
        self.view.refresh()
  