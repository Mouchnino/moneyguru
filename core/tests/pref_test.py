# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-06-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# Tests that make sure preferences are correctly saved/restored

from hsutil.testutil import eq_

from hsutil.testutil import with_tmpdir

from ..const import PaneType
from .base import TestApp, with_app, TestData

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
    app.doc.close()
    newapp = TestApp(app=app.app)
    # We have to load a file for the columns to be restored. That file doesn't have a 'foo' account
    newapp.doc.load_from_xml(TestData.filepath('moneyguru', 'simple.moneyguru')) # no crash on restore
    eq_(newapp.mw.pane_count, 5)
    # since we don't have enough tabs to restore last selected index, select the last one
    eq_(newapp.mw.current_pane_index, 4)

#--- Columns save/restore

def assert_column_save_restore(app, tablename, colname):
    table = getattr(app, tablename)
    table.columns.move_column(colname, 0)
    table.columns.resize_column(colname, 999)
    app.doc.close()
    newapp = TestApp(app=app.app)
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
@with_tmpdir
def test_expanded_nodes_are_restored_on_load(app, tmppath):
    # We can't use the normal compare_apps mechanism here because node expansion info doesn't go into
    # the document. This test also makes sure that the nodes expansion state are saved even if the
    # sheet is not connected at close (and thus doesn't receive the document_will_close msg).
    app.mw.select_income_statement()
    filepath = unicode(tmppath + 'foo.xml')
    app.doc.save_to_xml(filepath)
    app.doc.close()
    newapp = TestApp(app=app.app)
    newapp.doc.load_from_xml(filepath)
    assert (0, 0) in newapp.bsheet.expanded_paths
