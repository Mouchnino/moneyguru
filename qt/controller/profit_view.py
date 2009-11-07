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
from .profit_sheet import ProfitSheet
from .profit_graph import ProfitGraph
from ui.profit_view_ui import Ui_ProfitView

class ProfitView(BaseView, Ui_ProfitView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.psheet = ProfitSheet(doc=doc, view=self.treeView)
        self.pgraph = ProfitGraph(doc=doc, view=self.graphView)
        self.children = [self.psheet, self.pgraph]
    
    def _setupUi(self):
        self.setupUi(self)
    
