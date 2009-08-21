# Created By: Virgil Dupras
# Created On: 2009-08-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..base import TestCase, CommonSetup

class OneDailyScheduledTransaction(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.setup_scheduled_transaction(repeat_type_index=4, repeat_every=3)
        self.mainwindow.select_schedule_table()
    
    def test_attrs(self):
        eq_(len(self.sctable), 1)
        row = self.sctable[0]
        eq_(row.start_date, '13/09/2008')
        eq_(row.stop_date, '')
        eq_(row.repeat_type, 'Every second Saturday of the month')
        eq_(row.interval, '3')
        eq_(row.description, 'foobar')
    
    def test_delete(self):
        # calling delete() deletes the selected rows
        self.sctable.select([0])
        self.sctable.delete()
        eq_(len(self.sctable), 0)
        # And the spawns aren't there anymore in the ttable
        self.mainwindow.select_transaction_table()
        eq_(len(self.ttable), 0)
    
