# Created By: Virgil Dupras
# Created On: 2010-05-11
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.selectable_list import GUISelectableList

from ..const import PaneType
from .base import BaseView

class EmptyView(BaseView):
    VIEW_TYPE = PaneType.Empty
    
    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        plugin_names = [p.NAME for p in self.mainwindow.app.plugins]
        self.plugin_list = GUISelectableList(plugin_names)
    
    #--- Public
    def select_pane_type(self, pane_type):
        self.mainwindow.set_current_pane_type(pane_type)
    
    def open_selected_plugin(self):
        index = self.plugin_list.selected_index
        if index is None:
            return
        plugin = self.mainwindow.app.plugins[index]
        self.mainwindow.set_current_pane_with_plugin(plugin)
    
