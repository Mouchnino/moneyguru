# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from core.gui.custom_date_range_panel import CustomDateRangePanel as CustomDateRangePanelModel

from .panel import Panel
from ui.custom_date_range_panel_ui import Ui_CustomDateRangePanel

class CustomDateRangePanel(Panel, Ui_CustomDateRangePanel):
    FIELDS = [
        ('startDateEdit', 'start_date'),
        ('endDateEdit', 'end_date'),
        ('slotIndexComboBox', 'slot_index'),
        ('slotNameEdit', 'slot_name'),
    ]
    
    def __init__(self, parent, mainwindow):
        Panel.__init__(self, parent)
        self.setupUi(self)
        self.model = CustomDateRangePanelModel(view=self, mainwindow=mainwindow.model)
    
