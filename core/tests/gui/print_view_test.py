# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from ..base import TestCase
from ...gui.print_view import PrintView

class DateRangeOnApril2009(TestCase):
    def setUp(self):
        self.mock_today(2009, 4, 1)
        self.create_instances()
        self.drsel.select_month_range()
        self.pv = PrintView(self.tview)
    
    def test_attributes(self):
        # We don't bother testing other views, but they're expected to have PRINT_TITLE_FORMAT
        self.assertEqual(self.pv.title, 'Transactions from 01/04/2009 to 30/04/2009')
    
