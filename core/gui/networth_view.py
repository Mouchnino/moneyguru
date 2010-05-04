# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..const import ViewType
from .base import BaseView

class NetWorthView(BaseView):
    VIEW_TYPE = ViewType.NetWorth
    
    def __init__(self, view, mainwindow, children):
        BaseView.__init__(self, view, mainwindow.document, children)
        [self.bsheet, self.nwgraph, self.apie, self.lpie] = children
    
    #--- Public
    def delete_item(self):
        self.bsheet.delete()
    
    def new_item(self):
        self.bsheet.add_account()
    
    def new_group(self):
        self.bsheet.add_account_group()
    
    def show_account(self):
        self.bsheet.show_selected_account()
    
