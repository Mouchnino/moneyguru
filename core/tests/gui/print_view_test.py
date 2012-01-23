# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...gui.print_view import PrintView

class TestDateRangeOnApril2009:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2009, 4, 1)
        app = TestApp()
        app.drsel.select_month_range()
        app.pv = PrintView(app.tview)
        return app
    
    @with_app(do_setup)
    def test_attributes(self, app):
        # We don't bother testing other views, but they're expected to have PRINT_TITLE_FORMAT
        eq_(app.pv.title, 'Transactions from 01/04/2009 to 30/04/2009')
    
