# Created By: Virgil Dupras
# Created On: 2009-04-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from ..base import TestApp, with_app

@with_app(TestApp)
def test_monthly_xtickmark_dont_start_at_zero(app):
    # same as yearly, but with a month based date range
    app.drsel.select_custom_date_range()
    app.cdrpanel.start_date = '09/11/2007' # 22 days before the end of the month
    app.cdrpanel.end_date = '18/02/2008'
    app.cdrpanel.save() # changes the date range
    first_mark = app.nwgraph.xtickmarks[1] # 0 is xmin
    eq_(first_mark - app.nwgraph.xmin, 22)

@with_app(TestApp)
def test_yearly_xtickmark_dont_start_at_zero(app):
    # When you have a tickmark range that don't start at 0, don't make the whol X scale slide
    # rightwards. For example, if you had a multi-year range that don't start at the beginning
    # of the year, the first xtickmark would still be 365 days on the X line, making the data
    # and the marks not fitting together.
    app.drsel.select_custom_date_range()
    app.cdrpanel.start_date = '09/12/2007' # 23 days before the end of the year
    app.cdrpanel.end_date = '18/02/2009'
    app.cdrpanel.save() # changes the date range
    first_mark = app.nwgraph.xtickmarks[1] # 0 is xmin
    eq_(first_mark - app.nwgraph.xmin, 23)
    # also, don't make the label go left of the xmin
    assert app.nwgraph.xlabels[0]['pos'] >= app.nwgraph.xmin
