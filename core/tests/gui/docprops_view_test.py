# Created On: 2011/10/13
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_

from ...model.date import MonthRange
from ..base import ApplicationGUI, TestApp, with_app

#---
def app_props_shown():
    app = TestApp()
    app.show_dpview()
    return app

@with_app(app_props_shown)
def test_first_weekday_pref(app):
    # changing the first weekday affects the bar graphs as expected
    app.add_account('Asset')
    app.add_txn('31/12/2007', 'entry0', from_='Asset', to='Expense', amount='42')
    app.add_txn('1/1/2008', 'entry1', from_='Asset', to='Expense', amount='100')
    app.add_txn('20/1/2008', 'entry2', from_='Asset', to='Expense', amount='200')
    app.add_txn('31/3/2008', 'entry3', from_='Asset', to='Expense', amount='150')
    app.show_account('Expense')
    app.doc.date_range = MonthRange(date(2008, 1, 1))
    app.clear_gui_calls()
    app.dpview.first_weekday_list.select(1) # tuesday
    # The month conveniently starts on a tuesday, so the data now starts from the 1st of the month
    expected = [('01/01/2008', '08/01/2008', '100.00', '0.00'), 
                ('15/01/2008', '22/01/2008', '200.00', '0.00')]
    eq_(app.bar_graph_data(), expected)
    app.bargraph_gui.check_gui_calls(['refresh'])
    app.dpview.first_weekday_list.select(6) # sunday
    expected = [('30/12/2007', '06/01/2008', '142.00', '0.00'), 
                ('20/01/2008', '27/01/2008', '200.00', '0.00')]
    eq_(app.bar_graph_data(), expected)
