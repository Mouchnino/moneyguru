# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-11
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from moneyguru.gui.custom_date_range_panel import CustomDateRangePanel as CustomDateRangePanelModel

from .panel import Panel
from ui.custom_date_range_panel_ui import Ui_CustomDateRangePanel

#XXX This panel, on the model side doesn't use the general panel mechanism, which means that we have
# to do a hack to make it work. However, converting the panel would break the cocoa side, which I
# don't want to do at this time. But it has to be done at some point.
class CustomDateRangePanel(Panel, Ui_CustomDateRangePanel):
    def __init__(self, parent, doc):
        Panel.__init__(self, parent)
        self._setupUi()
        self.doc = doc
        self.model = CustomDateRangePanelModel(view=self, document=doc.model)
    
    def _loadFields(self):
        self.startDateEdit.setText(self.model.start_date)
        self.endDateEdit.setText(self.model.end_date)
    
    def _saveFields(self):
        self.model.start_date = unicode(self.startDateEdit.text())
        self.model.end_date = unicode(self.endDateEdit.text())
    
    def _setupUi(self):
        self.setupUi(self)
    
    #--- Hack
    def accept(self):
        self._saveFields()
        self.model.ok()
        QDialog.accept(self)
    
    def load(self):
        self.model.load()
        self._loadFields()
        self.show()
    
