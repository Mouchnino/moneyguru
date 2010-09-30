# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..const import PaneType
from ..trans import tr
from .base import BaseView

class BudgetView(BaseView):
    VIEW_TYPE = PaneType.Budget
    PRINT_TITLE_FORMAT = tr('Budgets from {start_date} to {end_date}')
    
    def set_children(self, children):
        BaseView.set_children(self, children)
        [self.btable] = children
    
    def delete_item(self):
        self.btable.delete()
    
