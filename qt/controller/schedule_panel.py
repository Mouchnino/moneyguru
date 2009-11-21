# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from moneyguru.gui.schedule_panel import SchedulePanel as SchedulePanelModel

from .panel import Panel
from .split_table import SplitTable
from ui.schedule_panel_ui import Ui_SchedulePanel

class SchedulePanel(Panel, Ui_SchedulePanel):
    def __init__(self, doc):
        Panel.__init__(self)
        self._setupUi()
        self.doc = doc
        self.model = SchedulePanelModel(view=self, document=doc.model)
        self.splitTable = SplitTable(transactionPanel=self, view=self.splitTableView)
        self.splitTable.model.connect()
        
        self.repeatTypeComboBox.currentIndexChanged.connect(self.repeatTypeChanged)
        self.repeatEverySpinBox.valueChanged.connect(self.repeatEveryChanged)
        self.startDateEdit.editingFinished.connect(self.startDateChanged)
    
    def _loadFields(self):
        self.startDateEdit.setText(self.model.start_date)
        self.repeatTypeComboBox.setCurrentIndex(self.model.repeat_type_index)
        self.repeatEverySpinBox.setValue(self.model.repeat_every)
        self.stopDateEdit.setText(self.model.stop_date)
        self.descriptionEdit.setText(self.model.description)
        self.payeeEdit.setText(self.model.payee)
        self.checkNoEdit.setText(self.model.checkno)
    
    def _saveFields(self):
        self.model.start_date = unicode(self.startDateEdit.text())
        self.model.repeat_type_index = self.repeatTypeComboBox.currentIndex()
        self.model.repeat_every = self.repeatEverySpinBox.value()
        self.model.stop_date = unicode(self.stopDateEdit.text())
        self.model.description = unicode(self.descriptionEdit.text())
        self.model.payee = unicode(self.payeeEdit.text())
        self.model.checkno = unicode(self.checkNoEdit.text())
    
    def _setupUi(self):
        self.setupUi(self)
    
    #--- Event Handlers
    def repeatTypeChanged(self, index):
        if self.repeatTypeComboBox.count() > 0: # don't change the value if the items have just been cleared.
            self.model.repeat_type_index = self.repeatTypeComboBox.currentIndex()
    
    def repeatEveryChanged(self, value):
        self.model.repeat_every = value
    
    def startDateChanged(self):
        self.model.start_date = unicode(self.startDateEdit.text())
    
    #--- model --> view
    def refresh_repeat_every(self):
        self.repeatEveryDescLabel.setText(self.model.repeat_every_desc)
    
    def refresh_repeat_options(self):
        self.repeatTypeComboBox.currentIndexChanged.disconnect(self.repeatTypeChanged)
        self.repeatTypeComboBox.clear()
        self.repeatTypeComboBox.addItems(self.model.repeat_options)
        self.repeatTypeComboBox.setCurrentIndex(self.model.repeat_type_index)
        self.repeatTypeComboBox.currentIndexChanged.connect(self.repeatTypeChanged)
    
