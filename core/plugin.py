# Created On: 2012/02/02
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.column import Column

from .gui.base import BaseView
from .gui.table import GUITable, Row
from .const import PaneType

class Plugin:
    NAME = ''
    
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.document = mainwindow.document
    
class ReadOnlyTableRow(Row):
    def set_field(self, name, value, sort_value=None):
        setattr(self, name, value)
        if sort_value is not None:
            setattr(self, '_'+name, sort_value)
        
    
class ReadOnlyTable(GUITable):
    def __init__(self, plugin):
        self.plugin = plugin
        self.COLUMNS = plugin.COLUMNS
        GUITable.__init__(self, plugin.document)
    
    def _fill(self):
        self.plugin.fill_table()
    

class ReadOnlyTableView(BaseView):
    VIEW_TYPE = PaneType.ReadOnlyTablePlugin
    
    def __init__(self, plugin):
        BaseView.__init__(self, plugin.mainwindow)
        self.plugin = plugin
        self.table = ReadOnlyTable(plugin)
        self.bind_messages(self.INVALIDATING_MESSAGES, self._revalidate)
    
    def _revalidate(self):
        self.table.refresh_and_show_selection()
    

class ReadOnlyTablePlugin(Plugin):
    COLUMNS = []
    
    def __init__(self, mainwindow):
        Plugin.__init__(self, mainwindow)
        self.view = ReadOnlyTableView(self)
        self.table = self.view.table
    
    def add_row(self):
        row = ReadOnlyTableRow(self.table)
        self.table.append(row)
        return row
    
    def fill_table(self):
        raise NotImplementedError()
    