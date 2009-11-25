# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.gui.schedule_table import ScheduleTable as ScheduleTableModel
from .column import Column
from .table import Table

class ScheduleTable(Table):
    COLUMNS = [
        Column('start_date', 'Start Date', 120),
        Column('stop_date', 'Stop Date', 120),
        Column('repeat_type', 'Repeat Type', 120),
        Column('interval', 'Interval', 80),
        Column('description', 'Description', 150),
        Column('payee', 'Payee', 150),
        Column('checkno', 'Check #', 100),
        Column('from_', 'From', 120),
        Column('to', 'To', 120),
        Column('amount', 'Amount', 120),
    ]
    
    def __init__(self, doc, view):
        model = ScheduleTableModel(view=self, document=doc.model)
        Table.__init__(self, model, view)
    
