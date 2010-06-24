# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt

from qtlib.column import Column
from core.gui.schedule_table import ScheduleTable as ScheduleTableModel
from core.trans import tr
from ..table import Table

class ScheduleTable(Table):
    COLUMNS = [
        Column('start_date', tr('Start Date'), 80),
        Column('stop_date', tr('Stop Date'), 80),
        Column('repeat_type', tr('Repeat Type'), 80),
        Column('interval', tr('Interval'), 50),
        Column('description', tr('Description'), 110),
        Column('payee', tr('Payee'), 110),
        Column('checkno', tr('Check #'), 70),
        Column('from_', tr('From'), 100),
        Column('to', tr('To'), 100),
        Column('amount', tr('Amount'), 97, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, schedule_view, view):
        model = ScheduleTableModel(view=self, schedule_view=schedule_view.model)
        Table.__init__(self, model, view)
        self.view.sortByColumn(0, Qt.AscendingOrder) # sorted by start_date by default
        self.view.deletePressed.connect(self.model.delete)
        self.view.doubleClicked.connect(self.model.edit)
        # we have to prevent Return from initiating editing.
        self.view.editSelected = lambda: None
    
