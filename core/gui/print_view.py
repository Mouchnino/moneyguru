# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..const import PaneType

class PrintView:
    def __init__(self, parent):
        self.parent = parent
        self.document = parent.document
        self.app = parent.app
    
    @property
    def title(self):
        if not hasattr(self.parent, 'PRINT_TITLE_FORMAT'):
            return ''
        if self.parent.VIEW_TYPE == PaneType.Account:
            account_name = self.parent.account.name
        title_format = self.parent.PRINT_TITLE_FORMAT
        start_date = self.app.format_date(self.document.date_range.start)
        end_date = self.app.format_date(self.document.date_range.end)
        return title_format.format(**locals())
    
