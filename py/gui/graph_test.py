# Unit Name: moneyguru.gui.graph_test
# Created By: Virgil Dupras
# Created On: 2009-04-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from ..main_test import TestCase

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_monthly_xtickmark_dont_start_at_zero(self):
        # same as yearly, but with a month based date range
        self.document.select_custom_date_range()
        self.cdrpanel.start_date = '09/11/2007' # 22 days before the end of the month
        self.cdrpanel.end_date = '18/02/2008'
        self.cdrpanel.ok() # changes the date range
        first_mark = self.nwgraph.xtickmarks[1] # 0 is xmin
        self.assertEqual(first_mark - self.nwgraph.xmin, 22)
    
    def test_yearly_xtickmark_dont_start_at_zero(self):
        # When you have a tickmark range that don't start at 0, don't make the whol X scale slide
        # rightwards. For example, if you had a multi-year range that don't start at the beginning
        # of the year, the first xtickmark would still be 365 days on the X line, making the data
        # and the marks not fitting together.
        self.document.select_custom_date_range()
        self.cdrpanel.start_date = '09/12/2007' # 23 days before the end of the year
        self.cdrpanel.end_date = '18/02/2009'
        self.cdrpanel.ok() # changes the date range
        first_mark = self.nwgraph.xtickmarks[1] # 0 is xmin
        self.assertEqual(first_mark - self.nwgraph.xmin, 23)
        # also, don't make the label go left of the xmin
        self.assertTrue(self.nwgraph.xlabels[0]['pos'] >= self.nwgraph.xmin)
    
