# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-08-16
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..base import TestCase, CommonSetup

class OneDailyScheduledTransactionLoaded(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.setup_scheduled_transaction()
        self.document.select_schedule_table()
        self.sctable.select([0])
        self.scpanel.load()
    
    def test_attrs(self):
        # The attributes of the panel are correctly set
        eq_(self.scpanel.start_date, '13/09/2008')
        eq_(self.scpanel.stop_date, '')
        eq_(self.scpanel.repeat_type_index, 0)
        eq_(self.scpanel.repeat_every, 3)
        eq_(self.scpanel.description, 'foobar')
    
    def test_edit_stop_date(self):
        # When editing stop date with an invalid date, just abort the edition. stop date is one
        # of those date field where a None value is possible.
        self.scpanel.stop_date = 'invalid' # no crash
        eq_(self.scpanel.stop_date, '') # None display value
    
    def test_edit_then_save(self):
        # Saving edits on the panel actually updates the schedule
        self.scpanel.stop_date = '15/09/2008'
        self.scpanel.repeat_every = 1
        self.scpanel.description = 'foobaz'
        self.scpanel.save()
        # To see if the save_edits() worked, we look if the spawns are correct in the ttable
        self.document.select_transaction_table()
        eq_(len(self.ttable), 3) #stops 2 days after it starts
