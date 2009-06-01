# Unit Name: moneyguru.gui.import_table
# Created By: Virgil Dupras
# Created On: 2008-08-08
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from .base import ImportWindowGUIObject
from .table import GUITable, Row

class ImportTable(ImportWindowGUIObject, GUITable):
    def __init__(self, view, import_window):
        ImportWindowGUIObject.__init__(self, view, import_window)
        GUITable.__init__(self)
        self.document = self.window.document
    
    #--- Override
    def connect(self):
        ImportWindowGUIObject.connect(self)
        self.refresh()
        self.view.refresh()
    
    #--- Public
    def bind(self, source_index, dest_index):
        source = self[source_index]
        dest = self[dest_index]
        source.bind(dest)
        self.refresh()
        self.view.refresh()
    
    def can_bind(self, source_index, dest_index):
        source = self[source_index]
        dest = self[dest_index]
        return source.can_bind(dest)
    
    def delete(self):
        rows = self.selected_rows
        for row in rows:
            row.will_import = False
        self.view.refresh()
    
    def refresh(self):
        del self[:]
        self.pane = self.window.selected_pane
        if not self.pane:
            return
        for exisiting, imported in self.pane.matches:
            self.append(ImportTableRow(self, exisiting, imported))
    
    def unbind(self, index):
        row = self[index]
        if not row.bound:
            return
        row.unbind()
        self.refresh()
        self.view.refresh()
    
    #--- Events
    def fields_switched(self):
        self.refresh()
        self.view.refresh()
        
    def pane_selected(self):
        self.refresh()
        self.view.refresh()
    

class ImportTableRow(Row):
    def __init__(self, table, entry, imported):
        Row.__init__(self, table)
        self.entry = entry
        self.imported = imported
        self.load()
    
    def bind(self, other):
        assert self.can_bind(other)
        existing = self.entry or other.entry
        imported = self.imported or other.imported
        self.table.pane.bind(existing, imported)
    
    def can_bind(self, other):
        return ((self.imported is None) != (other.imported is None)) and \
               ((self.entry is None) != (other.entry is None))
    
    def load(self):
        self._date = self.entry.date if self.entry else None
        self._description = self.entry.description if self.entry else ''
        self._amount = self.entry.amount if self.entry else None
        self._date_import = self.imported.date if self.imported else None
        self._description_import = self.imported.description if self.imported else ''
        self._payee_import = self.imported.payee if self.imported else ''
        self._checkno_import = self.imported.checkno if self.imported else ''
        self._transfer_import = ', '.join(s.name for s in self.imported.transfer) if self.imported else ''
        self._amount_import = self.imported.amount if self.imported else None
    
    def unbind(self):
        self.table.pane.unbind(self.entry, self.imported)
    
    #--- Properties
    @property
    def date(self):
        return self.table.document.app.format_date(self._date) if self._date else ''
    
    @property
    def description(self):
        return self._description
    
    @property
    def amount(self):
        return self.table.document.app.format_amount(self._amount)
    
    @property
    def bound(self):
        return self.entry is not None and self.imported is not None
    
    @property
    def date_import(self):
        return self.table.document.app.format_date(self._date_import) if self._date_import else ''
    
    @property
    def description_import(self):
        return self._description_import
    
    @property
    def payee_import(self):
        return self._payee_import
    
    @property
    def checkno_import(self):
        return self._checkno_import
    
    @property
    def transfer_import(self):
        return self._transfer_import
    
    @property
    def amount_import(self):
        return self.table.document.app.format_amount(self._amount_import)
    
    @property
    def can_edit_will_import(self):
        return self.imported is not None
    
    @property
    def will_import(self):
        return getattr(self.imported, 'will_import', True) if self.imported is not None else False
    
    @will_import.setter
    def will_import(self, value):
        if self.imported is not None:
            self.imported.will_import = value
    
