# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import QSize

from .base_view import BaseView
from .entry_table import EntryTable
from .account_bar_graph import AccountBarGraph
from .account_line_graph import AccountLineGraph
from support.line_graph_view import LineGraphView
from support.bar_graph_view import BarGraphView
from ui.entry_view_ui import Ui_EntryView

class EntryView(BaseView, Ui_EntryView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.etable = EntryTable(doc=doc, view=self.tableView)
        self.bgraph = AccountBarGraph(doc=doc, view=self.barGraphView)
        self.lgraph = AccountLineGraph(doc=doc, view=self.lineGraphView)
        # We don't add the graphs to self.children because connection/disconnection occur separately for them
        self.children = [self.etable]
    
    def _setupUi(self):
        self.setupUi(self)
    
    def showBarGraph(self):
        self.lgraph.model.disconnect()
        self.bgraph.model.connect()
        self.graphView.setCurrentIndex(1)
    
    def showLineGraph(self):
        self.bgraph.model.disconnect()
        self.lgraph.model.connect()
        self.graphView.setCurrentIndex(0)
    
