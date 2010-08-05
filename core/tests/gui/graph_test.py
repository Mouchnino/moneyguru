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

#--- One account
def app_one_account():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    return app

@with_app(app_one_account)
def test_balance_for_datapoints_are_computed_daily(app):
    # The balance went at 10000 with the first entry, but it went back to 1000 it with the second. 
    # The yaxis should only take the final 1000 into account
    app.add_entry(increase='10000')
    app.add_entry(decrease='9000') # same day
    eq_(app.balgraph.ymin, 900)
    eq_(app.balgraph.ymax, 1100)

@with_app(app_one_account)
def test_balance_goes_negative(app):
    # When the balance goes negative at some point, the yaxis follows.
    app.add_entry('3/10/2007', decrease='100')
    app.add_entry('4/10/2007', increase='200')
    eq_(app.balgraph.ymin, -200)
    eq_(app.balgraph.ymax, 200)
    eq_(list(app.balgraph.ytickmarks), range(-200, 201, 50))
    expected = [dict(text=str(x), pos=x) for x in range(-200, 201, 50)]
    eq_(list(app.balgraph.ylabels), expected)

@with_app(app_one_account)
def test_dont_go_negative_if_ymin_is_very_low(app):
    # If ymin is very low and we don't pay attention, the "wiggle room" the graph is giving might
    # make the y axis go negative when there's no negative value. Don't do that.
    app.add_entry(increase='1')
    eq_(app.balgraph.ymin, 0) # don't go negative!
    eq_(app.balgraph.ymax, 100)

@with_app(app_one_account)
def test_ymin_is_a_little_lower_than_lowest_datapoint(app):
    # When our lowest datapoint is exactly on factors, we end up with a graph showing nothing if
    # we don't lower the bar a little bit.
    app.add_entry(increase='1000') # exactly on the yfactor
    eq_(app.balgraph.ymin, 900) # one step lower
    eq_(app.balgraph.ymax, 1100) # one step higher
