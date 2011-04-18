# Created By: Virgil Dupras
# Created On: 2009-02-18
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...model.date import MonthRange

#--- Month range, panel loaded
def app_monthrange_panel_loaded():
    app = TestApp()
    app.doc.date_range = MonthRange(date(2007, 10, 1))
    app.drsel.select_custom_date_range()
    return app

@with_app(app_monthrange_panel_loaded)
def test_dates(app):
    # the dates, when loading the panel, are the dates of the current date range
    eq_(app.cdrpanel.start_date, '01/10/2007')
    eq_(app.cdrpanel.end_date, '31/10/2007')

@with_app(app_monthrange_panel_loaded)
def test_save_range(app):
    # Saving the date range under a slot adds it to drsel.
    app.cdrpanel.start_date = '17/03/2010'
    app.cdrpanel.slot_index = 1 # Slot 1
    app.cdrpanel.slot_name = 'foobar'
    app.cdrpanel.save()
    eq_(app.drsel.custom_range_names, ['foobar', None, None])

@with_app(app_monthrange_panel_loaded)
def test_set_start_later_than_end(app):
    # when start_date is set later than end_date, end_date is set to the same date.
    app.cdrpanel.start_date = '04/11/2007'
    eq_(app.cdrpanel.end_date, '04/11/2007')

@with_app(app_monthrange_panel_loaded)
def test_set_end_earlier_than_start(app):
    # when end_date is set earlier than start_date, start_date is set to the same date.
    app.cdrpanel.end_date = '04/09/2007'
    eq_(app.cdrpanel.start_date, '04/09/2007')
