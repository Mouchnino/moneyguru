# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..const import PaneType
from ..trans import tr
from .account_sheet_view import AccountSheetView

class NetWorthView(AccountSheetView):
    VIEW_TYPE = PaneType.NetWorth
    PRINT_TITLE_FORMAT = tr('Net Worth at {start_date}, starting from {end_date}')
    
    def set_children(self, children):
        AccountSheetView.set_children(self, children)
        [self.bsheet, self.nwgraph, self.apie, self.lpie] = children
    
