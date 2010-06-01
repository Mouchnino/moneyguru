# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-06-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# Tests that make sure preferences are correctly saved/restored

from nose.tools import eq_

from ..const import PaneType
from .base import TestApp, with_app

@with_app(TestApp)
def test_mainwindow_panes_reopen(app):
    # Main Window panes re-open themselves upon launch, in the same order
    app.mw.close_pane(4) # close budget pane
    app.add_account('foo')
    app.mw.show_account() # we now have the 'foo' account opened.
    app.mw.move_pane(4, 0) # move the 'foo' pane at the first index
    newapp = app.save_and_load()
    eq_(newapp.mw.current_pane_index, 0)
    newapp.check_current_pane(PaneType.Account, account_name='foo')
    newapp.mw.current_pane_index = 4
    newapp.check_current_pane(PaneType.Schedule)
