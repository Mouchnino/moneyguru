# Created By: Virgil Dupras
# Created On: 2009-08-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
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
        self.setup_scheduled_transaction(repeat_type_index=4, repeat_every=3, stop_date='13/12/2008')
        self.mainwindow.select_schedule_table()
        self.clear_gui_calls()
    
    def test_attrs(self):
        eq_(len(self.sctable), 1)
        row = self.sctable[0]
        eq_(row.start_date, '13/09/2008')
        eq_(row.stop_date, '13/12/2008')
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
    
    def test_edit_selected(self):
        # There was a bug where, although the selected_indexes in the table were correctly set
        # (to default values) on refresh(), the selection was not updated in the document.
        # This caused item edition not to work until the user manually selected a schedule.
        self.mainwindow.edit_item()
        self.check_gui_calls_partial(self.scpanel_gui, ['post_load'])
    
    def test_edition_must_stop(self):
        # When the edition_must_stop event is broadcasted, btable must ignore it because the objc
        # side doesn't have a stop_editing method.
        self.document.stop_edition()
        self.check_gui_calls_partial(self.sctable_gui, not_expected=['stop_editing'])
    
