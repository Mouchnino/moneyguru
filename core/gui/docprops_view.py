# Created On: 2011/10/13
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr

from ..const import PaneType
from .base import BaseView, LinkedSelectableList

class DocPropsView(BaseView):
    VIEW_TYPE = PaneType.DocProps
    INVALIDATING_MESSAGES = {'document_changed'}
    
    def __init__(self, view, mainwindow):
        BaseView.__init__(self, view, mainwindow)
        WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        WEEKDAYS = [tr(wd) for wd in WEEKDAYS]
        def setfunc(index):
            self.document.first_weekday = index
        self.first_weekday_list = LinkedSelectableList(items=WEEKDAYS, setfunc=setfunc)
        def setfunc(index):
            self.document.ahead_months = index
        self.ahead_months_list = LinkedSelectableList(items=list(map(str, range(12))), setfunc=setfunc)
        MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
            "September", "October", "November", "December"]
        MONTHS = [tr(wd) for wd in MONTHS]
        def setfunc(index):
            self.document.year_start_month = index + 1
        self.year_start_month_list = LinkedSelectableList(items=MONTHS, setfunc=setfunc)
        # temporary, once these are correctly set as document properties, we can normally remove this line below
        self._revalidate()
    
    def _revalidate(self):
        self.first_weekday_list.selected_index = self.document.first_weekday
        self.ahead_months_list.selected_index = self.document.ahead_months
        self.year_start_month_list.selected_index = self.document.year_start_month - 1
