# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.notify import Listener

class DocumentGUIObject(Listener):
    def __init__(self, view, document):
        Listener.__init__(self, document)
        self.view = view
        self.document = document
    
    @property
    def app(self):
        return self.document.app
    
    def account_added(self):
        pass
    
    def account_changed(self):
        pass

    def account_deleted(self):
        pass
    
    def account_needs_reassignment(self):
        pass
    
    def accounts_excluded(self):
        pass
    
    def account_must_be_shown(self):
        pass
    
    def csv_options_needed(self):
        pass
    
    def custom_date_range_selected(self):
        pass
    
    def date_range_changed(self):
        pass

    def date_range_will_change(self):
        pass
    
    def document_will_close(self):
        pass
    
    def edition_must_stop(self):
        pass
    
    def entries_imported(self):
        pass
    
    def entry_changed(self):
        pass

    def entry_deleted(self):
        pass
    
    def group_expanded_state_changed(self):
        pass
    
    def file_loaded_for_import(self):
        pass

    def file_loaded(self):
        pass
    
    def filter_applied(self):
        pass
    
    def first_weekday_changed(self):
        pass
    
    def reconciliation_changed(self):
        pass

    def redone(self):
        pass
    
    def schedule_changed(self):
        pass
    
    def schedule_deleted(self):
        pass
    
    def schedule_must_be_edited(self):
        pass
    
    def schedule_table_must_be_shown(self):
        pass
    
    def undone(self):
        pass

class TransactionPanelGUIObject(Listener):
    def __init__(self, view, panel):
        Listener.__init__(self, panel)
        self.view = view
        self.panel = panel
    
    def edition_must_stop(self):
        pass
    
    def panel_loaded(self):
        pass
    
    def split_changed(self):
        pass
    

class ImportWindowGUIObject(Listener):
    def __init__(self, view, window):
        Listener.__init__(self, window)
        self.view = view
        self.window = window
    
    def fields_switched(self):
        pass
    
    def pane_selected(self):
        pass
    
