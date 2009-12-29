# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.schedule_panel import SchedulePanel as SchedulePanelModel

from .panel import Panel
from .split_table import SplitTable
from ui.schedule_panel_ui import Ui_SchedulePanel

class SchedulePanel(Panel, Ui_SchedulePanel):
    FIELDS = [
        ('startDateEdit', 'start_date'),
        ('repeatTypeComboBox', 'repeat_type_index'),
        ('repeatEverySpinBox', 'repeat_every'),
        ('stopDateEdit', 'stop_date'),
        ('descriptionEdit', 'description'),
        ('payeeEdit', 'payee'),
        ('checkNoEdit', 'checkno'),
    ]
    
    def __init__(self, parent, doc):
        Panel.__init__(self, parent)
        self._setupUi()
        self.doc = doc
        self.model = SchedulePanelModel(view=self, document=doc.model)
        self.splitTable = SplitTable(transactionPanel=self, view=self.splitTableView)
        self.splitTable.model.connect()
        
        self.addSplitButton.clicked.connect(self.splitTable.model.add)
        self.removeSplitButton.clicked.connect(self.splitTable.model.delete)
        
    def _setupUi(self):
        self.setupUi(self)
    
    #--- model --> view
    def refresh_repeat_every(self):
        self.repeatEveryDescLabel.setText(self.model.repeat_every_desc)
    
    def refresh_repeat_options(self):
        self._changeComboBoxItems(self.repeatTypeComboBox, self.model.repeat_options)
    
