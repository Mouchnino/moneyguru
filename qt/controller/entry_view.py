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
from .entry_table import EntryTable
from ui.entry_view_ui import Ui_EntryView

class EntryView(BaseView, Ui_EntryView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.etable = EntryTable(doc=doc, view=self.tableView)
        self.children = [self.etable]
    
    def _setupUi(self):
        self.setupUi(self)
    
