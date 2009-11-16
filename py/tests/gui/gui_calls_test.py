# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-07
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# GUI calls are often made under the same conditions for multiple guis. Duplicating that condition
# in every test unit can get tedious, so this test unit is a "theme based" unit which tests calls
# made to GUIs' view.

from ..base import TestCase

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.check_gui_calls(self.bsheet_gui, refresh=1)
    
    def test_add_group(self):
        # Adding a group refreshes the view and goes into edit mode.
        self.bsheet.add_account_group()
        self.check_gui_calls(self.bsheet_gui, stop_editing=1, start_editing=1, refresh=1, update_selection=1)
    
    
class LoadFileWithBalanceSheetSelected(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
        self.document.load_from_xml(self.filepath('xml', 'moneyguru.xml'))
    
    def test_views_are_refreshed(self):
        # view.refresh() is called on file load
        self.check_gui_calls_partial(self.bsheet_gui, refresh=1)
        self.check_gui_calls_partial(self.nwgraph_gui, refresh=1)
    
