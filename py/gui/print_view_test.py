# Unit Name: moneyguru.gui.print_view_test
# Created By: Virgil Dupras
# Created On: 2009-04-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date

from ..main_test import TestCase, CommonSetup
from .print_view import PrintView

class DateRangeOnApril2009(TestCase, CommonSetup):
    def setUp(self):
        self.mock_today(2009, 04, 01)
        self.create_instances()
        self.setup_monthly_range()
        self.pv = PrintView(self.ttable)
    
    def test_attributes(self):
        self.assertEqual(self.pv.start_date, '01/04/2009')
        self.assertEqual(self.pv.end_date, '30/04/2009')
    
