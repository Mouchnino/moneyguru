# Created On: 2011/10/13
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
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
    app.dpview = app.show_dpview()
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

@with_app(app_props_shown)
def test_props_are_doc_based(app, tmpdir):
    # properties on dpview are document based, which means that they're saved in the document itself,
    # not in the preferences
    app.dpview.currency_list.select(42)
    app.dpview.first_weekday_list.select(4)
    app.dpview.ahead_months_list.select(5)
    app.dpview.year_start_month_list.select(6)
    fn = str(tmpdir.join('foo.moneyguru'))
    # We don't use TestApp.save_and_load() because we don't want to keep the app_gui instance,
    # which contains preference, to be sure that the data is actually doc-based
    app.doc.save_to_xml(fn)
    app = TestApp()
    app.doc.load_from_xml(fn)
    dpview = app.show_dpview()
    eq_(dpview.currency_list.selected_index, 42)
    eq_(dpview.first_weekday_list.selected_index, 4)
    eq_(dpview.ahead_months_list.selected_index, 5)
    eq_(dpview.year_start_month_list.selected_index, 6)

@with_app(app_props_shown)
def test_setting_prop_makes_doc_dirty(app):
    assert not app.doc.is_dirty()
    app.dpview.first_weekday_list.select(4)
    assert app.doc.is_dirty()
    
@with_app(app_props_shown)
def test_set_default_currency(app):
    app.dpview.currency_list.select(1) # EUR
    app.add_txn(amount='1')
    dpview = app.show_dpview()
    dpview.currency_list.select(0) # back to USD
    tview = app.show_tview()
    eq_(tview.ttable[0].amount, 'EUR 1.00')
