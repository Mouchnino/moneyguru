# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from ..const import PaneType
from .base import BaseView, MESSAGES_EVERYTHING_CHANGED
from .budget_table import BudgetTable

class BudgetView(BaseView):
    VIEW_TYPE = PaneType.Budget
    PRINT_TITLE_FORMAT = tr('Budgets from {start_date} to {end_date}')
    INVALIDATING_MESSAGES = MESSAGES_EVERYTHING_CHANGED | {'budget_changed', 'budget_deleted',
        'account_deleted'}
    
    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        self.table = BudgetTable(self)
        self.bind_messages(self.INVALIDATING_MESSAGES, self._revalidate)
    
    def _revalidate(self):
        self.table.refresh_and_show_selection()
    
    #--- Public
    def new_item(self):
        self.mainwindow.budget_panel.new()
    
    def edit_item(self):
        self.mainwindow.budget_panel.load()
    
    def delete_item(self):
        self.table.delete()
    
    #--- Events
    def document_will_close(self):
        self.table.columns.save_columns()
    
    def document_restoring_preferences(self):
        self.table.columns.restore_columns()
    
