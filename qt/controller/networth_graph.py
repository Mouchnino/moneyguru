# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.net_worth_graph import NetWorthGraph as NetWorthGraphModel
from support.graph_view import GraphView

class NetWorthGraph(object):
    def __init__(self, doc, view):
        self.doc = doc
        self.view = view
        self.model = NetWorthGraphModel(document=doc.model, view=self)
        self.view.dataSource = self.model
    
    #--- model --> view
    def refresh(self):
        self.view.update()
    
