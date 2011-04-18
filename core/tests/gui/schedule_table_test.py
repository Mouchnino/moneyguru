# Created By: Virgil Dupras
# Created On: 2009-08-12
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ...model.date import MonthRange
from ..base import TestApp

#--- One schedule
def app_schedule():
    app = TestApp()
    app.doc.date_range = MonthRange(app.app.parse_date('13/09/2008'))
    app.mainwindow.select_schedule_table()
    app.scpanel.new()
    app.scpanel.start_date = '13/09/2008'
    app.scpanel.description = 'foobar'
    app.scpanel.repeat_type_index = 4
    app.scpanel.repeat_every = 3
    app.scpanel.stop_date = '13/12/2008'
    app.scpanel.save()
    app.mainwindow.select_schedule_table()
    return app

def test_attrs():
    app = app_schedule()
    eq_(len(app.sctable), 1)
    row = app.sctable[0]
    eq_(row.start_date, '13/09/2008')
    eq_(row.stop_date, '13/12/2008')
    eq_(row.repeat_type, 'Every second Saturday of the month')
    eq_(row.interval, '3')
    eq_(row.description, 'foobar')

def test_delete():
    # calling delete() deletes the selected rows
    app = app_schedule()
    app.sctable.select([0])
    app.sctable.delete()
    eq_(len(app.sctable), 0)
    # And the spawns aren't there anymore in the ttable
    app.mainwindow.select_transaction_table()
    eq_(app.ttable.row_count, 0)

def test_edit_selected():
    # There was a bug where, although the selected_indexes in the table were correctly set
    # (to default values) on refresh(), the selection was not updated in the document.
    # This caused item edition not to work until the user manually selected a schedule.
    app = app_schedule()
    app.clear_gui_calls()
    app.mainwindow.edit_item()
    app.check_gui_calls_partial(app.scpanel_gui, ['post_load'])

def test_edition_must_stop():
    # When the edition_must_stop event is broadcasted, btable must ignore it because the objc
    # side doesn't have a stop_editing method.
    app = app_schedule()
    app.clear_gui_calls()
    app.doc.stop_edition()
    app.check_gui_calls_partial(app.sctable_gui, not_expected=['stop_editing'])
