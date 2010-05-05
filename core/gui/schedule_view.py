# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..const import PaneType
from .base import BaseView

class ScheduleView(BaseView):
    VIEW_TYPE = PaneType.Schedule
    
    def set_children(self, children):
        BaseView.set_children(self, children)
        [self.sctable] = children
    
    def delete_item(self):
        self.sctable.delete()
    
