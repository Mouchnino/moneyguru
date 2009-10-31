# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base_view import BaseView
from .transaction_table import TransactionTable
from ui.transaction_view_ui import Ui_TransactionView

class TransactionView(BaseView, Ui_TransactionView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.ttable = TransactionTable(doc=doc, view=self.tableView)
        self.children = [self.ttable]
    
    def _setupUi(self):
        self.setupUi(self)
    