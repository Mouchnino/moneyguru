# Created By: Virgil Dupras
# Created On: 2010-05-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..const import PaneType
from .base import BaseView

class EmptyView(BaseView):
    VIEW_TYPE = PaneType.Empty
    
    #--- Public
    def select_pane_type(self, pane_type):
        self.mainwindow.set_current_pane_type(pane_type)
    
