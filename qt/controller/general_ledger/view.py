# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.general_ledger_view import GeneralLedgerView as GeneralLedgerViewModel

from ..base_view import BaseView
from .table import GeneralLedgerTable
from ui.general_ledger_view_ui import Ui_GeneralLedgerView

class GeneralLedgerView(BaseView, Ui_GeneralLedgerView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = GeneralLedgerViewModel(view=self, mainwindow=mainwindow.model)
        self.gltable = GeneralLedgerTable(self, view=self.tableView)
        children = [self.gltable.model]
        self.model.set_children(children)
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.gltable.restoreColumns()
    
    #--- QWidget override
    def setFocus(self):
        self.gltable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.gltable)
    