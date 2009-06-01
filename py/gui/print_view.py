# Unit Name: moneyguru.gui.print_view
# Created By: Virgil Dupras
# Created On: 2009-04-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

class PrintView(object):
    def __init__(self, parent):
        self.parent = parent
        self.document = parent.document
        self.app = parent.app
    
    @property
    def start_date(self):
        return self.app.format_date(self.document.date_range.start)
    
    @property
    def end_date(self):
        return self.app.format_date(self.document.date_range.end)
    