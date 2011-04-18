# Created By: Virgil Dupras
# Created On: 2009-11-27
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.document import FilterType
from core.gui.filter_bar import EntryFilterBar as EntryFilterBarModel
from hscommon.trans import tr

from ..filter_bar import FilterBar

class EntryFilterBar(FilterBar):
    BUTTONS = [
        (tr("All"), None),
        (tr("Increase"), FilterType.Income),
        (tr("Decrease"), FilterType.Expense),
        (tr("Transfers"), FilterType.Transfer),
        (tr("Unassigned"), FilterType.Unassigned),
        (tr("Reconciled"), FilterType.Reconciled),
        (tr("Not Reconciled"), FilterType.NotReconciled),
    ]
    
    def __init__(self, account_view, view):
        model = EntryFilterBarModel(account_view=account_view.model, view=self)
        FilterBar.__init__(self, model, view)
    
    #--- model --> view
    def disable_transfers(self):
        self.view.buttons[3].setEnabled(False)
    
    def enable_transfers(self):
        self.view.buttons[3].setEnabled(True)
    
