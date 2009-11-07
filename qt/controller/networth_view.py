# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base_view import BaseView
from .networth_sheet import NetWorthSheet
from .networth_graph import NetWorthGraph
from ui.sheet_view_ui import Ui_SheetView

class NetWorthView(BaseView, Ui_SheetView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.nwsheet = NetWorthSheet(doc=doc, view=self.treeView)
        self.nwgraph = NetWorthGraph(doc=doc, view=self.graphView)
        self.children = [self.nwsheet, self.nwgraph]
    
    def _setupUi(self):
        self.setupUi(self)
    
