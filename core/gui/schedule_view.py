# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from ..const import PaneType
from .base import BaseView, MESSAGES_EVERYTHING_CHANGED
from .schedule_table import ScheduleTable

class ScheduleView(BaseView):
    VIEW_TYPE = PaneType.Schedule
    PRINT_TITLE_FORMAT = tr('Schedules from {start_date} to {end_date}')
    INVALIDATING_MESSAGES = MESSAGES_EVERYTHING_CHANGED | {'schedule_changed', 'schedule_deleted',
        'account_deleted'}
    
    def __init__(self, view, mainwindow):
        BaseView.__init__(self, view, mainwindow)
        self.table = ScheduleTable(self)
        self.columns = self.table.columns
        self.bind_messages(self.INVALIDATING_MESSAGES, self._revalidate)
    
    def _revalidate(self):
        self.table.refresh_and_show_selection()
    
    #--- Public
    def new_item(self):
        self.mainwindow.schedule_panel.new()
    
    def edit_item(self):
        self.mainwindow.schedule_panel.load()
    
    def delete_item(self):
        self.table.delete()
    
    #--- Events
    def document_will_close(self):
        self.table.columns.save_columns()
    
    def document_restoring_preferences(self):
        self.table.columns.restore_columns()
    
