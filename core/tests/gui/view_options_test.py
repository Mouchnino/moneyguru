# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-07-27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..base import TestApp, with_app

#--- Pristine
@with_app(TestApp)
def test_column_visibility_change_actually_changes_visibility(app):
    # Changing the value of a column visibility in view options actually changes visibility
    app.vopts.transaction_table_description = False
    assert not app.ttable.columns.column_is_visible('description')

@with_app(TestApp)
def test_change_view_options_while_editing(app):
    # When a table is in editing mode and that a column visibility is changed, we have to tell the
    # gui to stop editing, or else we end up in a state where the core thinks it's editing when the
    # GUI isn't.
    app.show_tview()
    app.mw.new_item()
    app.ttable.payee = 'something' # in editing mode
    app.vopts.transaction_table_description = False
    assert app.ttable.edited is None
