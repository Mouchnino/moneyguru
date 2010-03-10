# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-08-16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ...model.date import MonthRange
from ..base import TestCase, CommonSetup, TestApp

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_schedule_table()
    
    def test_add_schedule(self):
        self.scpanel.new()
        self.scpanel.description = 'foobar'
        self.scpanel.save()
        eq_(len(self.sctable), 1)
        eq_(self.sctable[0].description, 'foobar')
    
    def test_edit_schedule(self):
        # Initiating a schedule edition while none is selected doesn't crash
        self.mainwindow.edit_item() # no crash
    

class OneDailyScheduledTransaction(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(repeat_every=3)
        self.mainwindow.select_schedule_table()
        self.sctable.select([0])
        self.clear_gui_calls()
    
    def test_calls_refresh_repeat_every_on_load(self):
        # When the panel loads, make the panel call its refresh_repeat_every() view method so that
        # the correct time unit escription shows up
        self.scpanel.load()
        self.check_gui_calls_partial(self.scpanel_gui, ['refresh_repeat_every'])
    
    def test_repeat_every(self):
        # changing repeat every makes the desc plural if appropriate
        self.assertEqual(self.scpanel.repeat_every, 3)
        self.assertEqual(self.scpanel.repeat_every_desc, 'days')
    
    def test_repeat_type_index(self):
        # changing the repeat_type_index changes the repeat_every_desc attribute
        self.assertEqual(self.scpanel.repeat_every_desc, 'days')
        self.scpanel.repeat_every = 1
        self.assertEqual(self.scpanel.repeat_every_desc, 'day')
        self.check_gui_calls(self.scpanel_gui, ['refresh_repeat_every'])
        self.scpanel.repeat_type_index = 1
        self.assertEqual(self.scpanel.repeat_every_desc, 'week')
        self.scpanel.repeat_type_index = 2
        self.assertEqual(self.scpanel.repeat_every_desc, 'month')
        self.scpanel.repeat_type_index = 3
        self.assertEqual(self.scpanel.repeat_every_desc, 'year')
        self.scpanel.repeat_type_index = 4
        self.assertEqual(self.scpanel.repeat_every_desc, 'month')
        self.scpanel.repeat_type_index = 5
        self.assertEqual(self.scpanel.repeat_every_desc, 'month')
    
    def test_repeat_options(self):
        # Repeat options depend on the txn's date. 13/09/2008 is the second saturday of July.
        expected = ['Daily', 'Weekly', 'Monthly', 'Yearly', 'Every second Saturday of the month']
        self.assertEqual(self.scpanel.repeat_options, expected)
    
    def test_repeat_options_on_last_week(self):
        # When the txn's date is on the last week of the month, there's an extra 'last' option
        self.scpanel.start_date = '29/07/2008'
        expected = ['Daily', 'Weekly', 'Monthly', 'Yearly', 'Every fifth Tuesday of the month',
                    'Every last Tuesday of the month']
        self.assertEqual(self.scpanel.repeat_options, expected)
        self.check_gui_calls(self.scpanel_gui, ['refresh_repeat_options'])
    

#--- Daily schedule loaded
def app_daily_schedule_loaded():
    app = TestApp()
    app.doc.date_range = MonthRange(app.app.parse_date('13/09/2008'))
    app.mainwindow.select_schedule_table()
    app.scpanel.new()
    app.scpanel.start_date = '13/09/2008'
    app.scpanel.description = 'foobar'
    app.scpanel.repeat_type_index = 0
    app.scpanel.repeat_every = 3
    app.scpanel.notes = 'some notes'
    app.scpanel.save()
    app.mainwindow.select_schedule_table()
    app.sctable.select([0])
    app.scpanel.load()
    return app
    
def test_attrs():
    # The attributes of the panel are correctly set
    app = app_daily_schedule_loaded()
    eq_(app.scpanel.start_date, '13/09/2008')
    eq_(app.scpanel.stop_date, '')
    eq_(app.scpanel.repeat_type_index, 0)
    eq_(app.scpanel.repeat_every, 3)
    eq_(app.scpanel.description, 'foobar')
    eq_(app.scpanel.notes, 'some notes')

def test_edit_stop_date():
    # When editing stop date with an invalid date, just abort the edition. stop date is one
    # of those date field where a None value is possible.
    app = app_daily_schedule_loaded()
    app.scpanel.stop_date = 'invalid' # no crash
    eq_(app.scpanel.stop_date, '') # None display value

def test_edit_then_save():
    # Saving edits on the panel actually updates the schedule
    app = app_daily_schedule_loaded()
    app.scpanel.stop_date = '15/09/2008'
    app.scpanel.repeat_every = 1
    app.scpanel.description = 'foobaz'
    app.scpanel.save()
    # To see if the save_edits() worked, we look if the spawns are correct in the ttable
    app.mainwindow.select_transaction_table()
    eq_(app.ttable.row_count, 3) #stops 2 days after it starts
