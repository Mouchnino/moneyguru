# Created By: Virgil Dupras
# Created On: 2009-08-16
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ...model.date import MonthRange
from ..base import TestApp, with_app

@with_app(TestApp)
def test_add_schedule(app):
    app.show_scview()
    app.scpanel.new()
    app.scpanel.description = 'foobar'
    app.scpanel.save()
    eq_(len(app.sctable), 1)
    eq_(app.sctable[0].description, 'foobar')

@with_app(TestApp)
def test_edit_schedule(app):
    # Initiating a schedule edition while none is selected doesn't crash
    app.show_scview()
    app.mainwindow.edit_item() # no crash

#---
def app_daily_scheduled_txn():
    app = TestApp()
    app.add_schedule(start_date='13/09/2008', repeat_every=3)
    app.sctable.select([0])
    app.clear_gui_calls()
    return app

@with_app(app_daily_scheduled_txn)
def test_calls_refresh_repeat_every_on_load(app):
    # When the panel loads, make the panel call its refresh_repeat_every() view method so that
    # the correct time unit escription shows up
    app.scpanel.load()
    app.scpanel.view.check_gui_calls_partial(['refresh_repeat_every'])

@with_app(app_daily_scheduled_txn)
def test_repeat_every(app):
    # changing repeat every makes the desc plural if appropriate
    eq_(app.scpanel.repeat_every, 3)
    eq_(app.scpanel.repeat_every_desc, 'days')

@with_app(app_daily_scheduled_txn)
def test_repeat_type_index(app):
    # changing the repeat_type_index changes the repeat_every_desc attribute
    eq_(app.scpanel.repeat_every_desc, 'days')
    app.scpanel.repeat_every = 1
    eq_(app.scpanel.repeat_every_desc, 'day')
    app.scpanel.view.check_gui_calls(['refresh_repeat_every'])
    app.scpanel.repeat_type_list.select(1)
    eq_(app.scpanel.repeat_every_desc, 'week')
    app.scpanel.repeat_type_list.select(2)
    eq_(app.scpanel.repeat_every_desc, 'month')
    app.scpanel.repeat_type_list.select(3)
    eq_(app.scpanel.repeat_every_desc, 'year')
    app.scpanel.repeat_type_list.select(4)
    eq_(app.scpanel.repeat_every_desc, 'month')
    app.scpanel.repeat_type_list.select(5)
    eq_(app.scpanel.repeat_every_desc, 'month')

@with_app(app_daily_scheduled_txn)
def test_repeat_options(app):
    # Repeat options depend on the txn's date. 13/09/2008 is the second saturday of July.
    expected = ['Daily', 'Weekly', 'Monthly', 'Yearly', 'Every second Saturday of the month']
    eq_(app.scpanel.repeat_type_list[:], expected)

@with_app(app_daily_scheduled_txn)
def test_repeat_options_on_last_week(app):
    # When the txn's date is on the last week of the month, there's an extra 'last' option
    app.scpanel.start_date = '29/07/2008'
    expected = ['Daily', 'Weekly', 'Monthly', 'Yearly', 'Every fifth Tuesday of the month',
                'Every last Tuesday of the month']
    eq_(app.scpanel.repeat_type_list[:], expected)
    app.scpanel.repeat_type_list.view.check_gui_calls(['refresh'])

#--- Daily schedule loaded
def app_daily_schedule_loaded():
    app = TestApp()
    app.doc.date_range = MonthRange(app.app.parse_date('13/09/2008'))
    app.show_scview()
    app.scpanel.new()
    app.scpanel.start_date = '13/09/2008'
    app.scpanel.description = 'foobar'
    app.scpanel.repeat_type_list.select(0)
    app.scpanel.repeat_every = 3
    app.scpanel.notes = 'some notes'
    app.scpanel.save()
    app.show_scview()
    app.sctable.select([0])
    app.scpanel.load()
    return app
    
def test_attrs():
    # The attributes of the panel are correctly set
    app = app_daily_schedule_loaded()
    eq_(app.scpanel.start_date, '13/09/2008')
    eq_(app.scpanel.stop_date, '')
    eq_(app.scpanel.repeat_type_list.selected_index, 0)
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
    app.show_tview()
    eq_(app.ttable.row_count, 3) #stops 2 days after it starts
