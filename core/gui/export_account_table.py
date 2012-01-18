# Created By: Virgil Dupras
# Created On: 2010-10-24
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import trget
from hscommon.gui.column import Column
from ..model.account import ACCOUNT_SORT_KEY
from .table import GUITable, Row

trcol = trget('columns')

class ExportAccountTable(GUITable):
    COLUMNS = [
        Column('name', display=trcol("Account")),
        Column('export', display=trcol("Export")),
    ]
    
    def __init__(self, export_panel):
        self.panel = export_panel
        GUITable.__init__(self, document=export_panel.document)
    
    #--- Override
    def _fill(self):
        accounts = sorted(self.panel.accounts, key=ACCOUNT_SORT_KEY)
        for account in accounts:
            self.append(ExportAccountTableRow(self, account))
    

class ExportAccountTableRow(Row):
    def __init__(self, table, account):
        Row.__init__(self, table)
        self.account = account
    
    #--- Public
    def load(self):
        pass # nothing to load
    
    def save(self):
        pass # read-only
    
    #--- Properties
    @property
    def name(self):
        return self.account.name
    
    @property
    def export(self):
        return self.table.panel.is_exported(self.account.name)
    
    @export.setter
    def export(self, value):
        self.table.panel.set_exported(self.account.name, value)
    
