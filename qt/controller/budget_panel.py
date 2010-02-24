# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.budget_panel import BudgetPanel as BudgetPanelModel

from .panel import Panel
from ui.budget_panel_ui import Ui_BudgetPanel

class BudgetPanel(Panel, Ui_BudgetPanel):
    FIELDS = [
        ('startDateEdit', 'start_date'),
        ('repeatTypeComboBox', 'repeat_type_index'),
        ('repeatEverySpinBox', 'repeat_every'),
        ('stopDateEdit', 'stop_date'),
        ('accountComboBox', 'account_index'),
        ('targetComboBox', 'target_index'),
        ('amountEdit', 'amount'),
        ('notesEdit', 'notes'),
    ]
    
    def __init__(self, parent, doc):
        Panel.__init__(self, parent)
        self._setupUi()
        self.doc = doc
        self.model = BudgetPanelModel(view=self, document=doc.model)
        
    def _setupUi(self):
        self.setupUi(self)
    
    def _loadFields(self):
        self._changeComboBoxItems(self.accountComboBox, self.model.account_options)
        self._changeComboBoxItems(self.targetComboBox, self.model.target_options)
        Panel._loadFields(self)
    
    #--- model --> view
    def refresh_repeat_every(self):
        self.repeatEveryDescLabel.setText(self.model.repeat_every_desc)
    
    def refresh_repeat_options(self):
        self._changeComboBoxItems(self.repeatTypeComboBox, self.model.repeat_options)
    