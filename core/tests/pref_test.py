# Created By: Virgil Dupras
# Created On: 2010-06-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# Tests that make sure preferences are correctly saved/restored

from hscommon.testutil import eq_

from ..const import PaneType
from ..gui.main_window import OPENED_PANES_PREFERENCE
from .base import TestApp, with_app, testdata

#--- Pristine
@with_app(TestApp)
def test_mainwindow_panes_reopen(app):
    # Main Window panes re-open themselves upon launch, in the same order
    app.mw.close_pane(4) # close budget pane
    app.add_account('foo')
    app.mw.show_account() # we now have the 'foo' account opened.
    app.mw.move_pane(4, 1) # move the 'foo' pane at the second position
    # The selected pane index is 1
    newapp = app.save_and_load()
    eq_(newapp.mw.current_pane_index, 1) # We've restored the selected pane index
    newapp.check_current_pane(PaneType.Account, account_name='foo')
    newapp.mw.current_pane_index = 4
    newapp.check_current_pane(PaneType.Schedule)

@with_app(TestApp)
def test_mainwindow_panes_reopen_except_nonexistant_accounts(app):
    # When re-opening tabs, ignore (and don't crash) tabs for accounts that aren't in the document.
    app.add_account('foo')
    app.mw.show_account()
    filename = app.save_file()
    app.doc.close()
    # now, we're going to remove the account from underneath
    meddling_app = TestApp()
    meddling_app.doc.load_from_xml(filename)
    meddling_app.bsheet.selected = meddling_app.bsheet.assets[0]
    meddling_app.bsheet.delete()
    meddling_app.doc.save_to_xml(filename)
    newapp = TestApp(app=app.app)
    # We have to load a file for the columns to be restored. That file doesn't have a 'foo' account
    newapp.doc.load_from_xml(filename) # no crash on restore
    eq_(newapp.mw.pane_count, 5)
    # since we don't have enough tabs to restore last selected index, select the last one
    eq_(newapp.mw.current_pane_index, 4)

@with_app(TestApp)
def test_main_window_doent_choke_on_unexisting_pane_pref(app):
    app.app.set_default(OPENED_PANES_PREFERENCE, [{'pane_type': '99999'}])
    newapp = TestApp(app=app.app)
    newapp.doc.load_from_xml(testdata.filepath('moneyguru', 'simple.moneyguru')) # no crash on restore
    newapp.check_current_pane(PaneType.NetWorth) # been replaced with a Net Worth pane.

@with_app(TestApp)
def test_gui_calls_after_pref_restore(app):
    # appropriate gui calls are made after pref restore
    app.clear_gui_calls()
    app = app.save_and_load()
    app.check_gui_calls(app.ttablecol_gui, ['restore_columns'])
    app.check_gui_calls_partial(app.bsheet_gui, ['refresh_expanded_paths'])

#--- Columns save/restore
def assert_column_save_restore(app, tablename, colname):
    table = getattr(app, tablename)
    table.columns.move_column(colname, 0)
    table.columns.resize_column(colname, 999)
    newapp = app.save_and_load()
    table = getattr(newapp, tablename)
    eq_(table.columns.colnames[0], colname)
    eq_(table.columns.column_width(colname), 999)

@with_app(TestApp)
def test_ttable_restores_columns(app):
    assert_column_save_restore(app, 'ttable', 'payee')

@with_app(TestApp)
def test_etable_restores_columns(app):
    assert_column_save_restore(app, 'etable', 'payee')

@with_app(TestApp)
def test_sctable_restores_columns(app):
    assert_column_save_restore(app, 'sctable', 'payee')

@with_app(TestApp)
def test_btable_restores_columns(app):
    assert_column_save_restore(app, 'btable', 'target')

@with_app(TestApp)
def test_bsheet_restores_columns(app):
    assert_column_save_restore(app, 'bsheet', 'end')

@with_app(TestApp)
def test_istatement_restores_columns(app):
    assert_column_save_restore(app, 'istatement', 'last_cash_flow')

#--- Expanded group
def app_expanded_group():
    app = TestApp()
    app.add_group('group')
    app.bsheet.expand_node(app.bsheet.assets[0])
    return app

@with_app(app_expanded_group)
def test_expanded_nodes_are_restored_on_load(app):
    # We can't use the normal compare_apps mechanism here because node expansion info doesn't go into
    # the document. This test also makes sure that the nodes expansion state are saved even if the
    # sheet is not connected at close (and thus doesn't receive the document_will_close msg).
    app.mw.select_income_statement()
    newapp = app.save_and_load()
    assert (0, 0) in newapp.bsheet.expanded_paths

#--- Two different documents
def test_expanded_node_prefs_is_at_document_level():
    # Expanded node preferences are at the document level
    app1 = TestApp()
    app1.add_group('group')
    app1.bsheet.expand_node(app1.bsheet.assets[0])
    filename = app1.save_file()
    app1.doc.close()
    app2 = TestApp(app=app1.app)
    app2.add_group('group')
    app2.bsheet.collapse_node(app1.bsheet.assets[0])
    app2.doc.close() # when not doc based, this call will overwrite first doc's prefs
    newapp = TestApp(app=app1.app)
    newapp.doc.load_from_xml(filename)
    assert (0, 0) in newapp.bsheet.expanded_paths

def test_table_column_prefs_is_at_document_level():
    # table columns preferences are at the document level
    app1 = TestApp()
    app1.ttable.columns.move_column('date', 5)
    app1.ttable.columns.resize_column('date', 42)
    app1.ttable.columns.set_column_visible('date', False)
    filename = app1.save_file()
    app1.doc.close()
    app2 = TestApp(app=app1.app)
    app2.ttable.columns.move_column('date', 4)
    app2.ttable.columns.resize_column('date', 41)
    app2.ttable.columns.set_column_visible('date', True)
    app2.doc.close()
    newapp = TestApp(app=app1.app)
    newapp.doc.load_from_xml(filename)
    eq_(newapp.ttable.columns.colnames[5], 'date')
    eq_(newapp.ttable.columns.column_width('date'), 42)
    assert not newapp.ttable.columns.column_is_visible('date')

def test_account_exclusion_prefs_is_at_document_level():
    # account exclusion preferences are at the document level
    app1 = TestApp()
    app1.add_account('foo')
    app1.bsheet.toggle_excluded()
    filename = app1.save_file()
    app1.doc.close()
    app2 = TestApp(app=app1.app)
    app2.add_account('foo')
    app2.doc.close()
    newapp = TestApp(app=app1.app)
    newapp.doc.load_from_xml(filename)
    assert newapp.bsheet.assets[0].is_excluded

def test_pane_prefs_is_at_document_level():
    # pane preferences are at the document level
    app1 = TestApp()
    app1.mw.close_pane(4) # close budget pane
    filename = app1.save_file()
    app1.doc.close()
    app2 = TestApp(app=app1.app)
    app1.mw.close_pane(3) # close schedule pane
    app2.doc.close()
    newapp = TestApp(app=app1.app)
    newapp.doc.load_from_xml(filename)
    eq_(newapp.mw.pane_count, 4)
    newapp.mw.current_pane_index = 3
    newapp.check_current_pane(PaneType.Schedule)
