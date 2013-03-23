# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt

from qtlib.column import Column
from ..table import Table

class BudgetTable(Table):
    COLUMNS = [
        Column('start_date', 90),
        Column('stop_date', 90),
        Column('repeat_type', 80),
        Column('interval', 50),
        Column('account', 144),
        Column('target', 144),
        Column('amount', 100, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, model, view):
        Table.__init__(self, model, view)
        self.view.sortByColumn(0, Qt.AscendingOrder) # sorted by start_date by default
        self.view.deletePressed.connect(self.model.delete)
        self.view.doubleClicked.connect(self.model.edit)
        # we have to prevent Return from initiating editing.
        self.view.editSelected = lambda: None
    
