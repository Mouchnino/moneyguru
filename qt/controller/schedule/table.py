# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt

from core.gui.schedule_table import ScheduleTable as ScheduleTableModel
from ..column import Column
from ..table import Table

class ScheduleTable(Table):
    COLUMNS = [
        Column('start_date', 'Start Date', 80),
        Column('stop_date', 'Stop Date', 80),
        Column('repeat_type', 'Repeat Type', 80),
        Column('interval', 'Interval', 50),
        Column('description', 'Description', 110),
        Column('payee', 'Payee', 110),
        Column('checkno', 'Check #', 70),
        Column('from_', 'From', 100),
        Column('to', 'To', 100),
        Column('amount', 'Amount', 97, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, doc, view):
        model = ScheduleTableModel(view=self, document=doc.model)
        Table.__init__(self, model, view)
        self.view.sortByColumn(0, Qt.AscendingOrder) # sorted by start_date by default
        self.view.deletePressed.connect(self.model.delete)
        self.view.doubleClicked.connect(self.model.edit)
    
