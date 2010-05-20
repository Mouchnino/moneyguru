# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.notify import Listener, Repeater

class DocumentNotificationsMixin(object):
    def account_added(self):
        pass
    
    def account_changed(self):
        pass

    def account_deleted(self):
        pass
    
    def accounts_excluded(self):
        pass
    
    def budget_changed(self):
        pass
    
    def budget_deleted(self):
        pass
    
    def csv_options_needed(self):
        pass
    
    def custom_date_range_selected(self):
        pass
    
    def date_range_changed(self):
        pass

    def date_range_will_change(self):
        pass
    
    # When the whole document changed
    def document_changed(self): 
        pass
    
    def document_will_close(self):
        pass
    
    def edition_must_stop(self):
        pass
    
    # A file has been parsed and is ready to be shown to the user in the import window
    def file_loaded_for_import(self):
        pass
    
    def filter_applied(self):
        pass
    
    # The First Weekday preferences has been changed
    def first_weekday_changed(self): 
        pass
    
    def performed_undo_or_redo(self):
        pass
    
    def saved_custom_ranges_changed(self):
        pass
    
    def schedule_changed(self):
        pass
    
    def schedule_deleted(self):
        pass
    
    def transaction_changed(self):
        pass
    
    def transaction_deleted(self):
        pass
    
    def transactions_imported(self):
        pass
    

class MainWindowNotificationsMixin(object):
    def transactions_selected(self):
        pass
    

class SheetViewNotificationsMixin(object):
    def group_expanded_state_changed(self):
        pass
    

class HideableObject(object):
    INVALIDATING_MESSAGES = set()
    
    def __init__(self):
        self._hidden = True
        self._invalidated = True
    
    #--- Protected
    def _process_message(self, msg):
        if msg in self.INVALIDATING_MESSAGES:
            self._invalidated = True
    
    def _revalidate(self):
        pass
    
    #--- Public
    def show(self):
        self._hidden = False
        if self._invalidated:
            self._revalidate()
            self._invalidated = False
    
    def hide(self):
        self._hidden = True
    

class DocumentGUIObject(Listener, DocumentNotificationsMixin):
    def __init__(self, view, document):
        Listener.__init__(self, document)
        self.view = view
        self.document = document
    
    @property
    def app(self):
        return self.document.app
    

class ViewChild(Listener, HideableObject, DocumentNotificationsMixin, MainWindowNotificationsMixin):
    # yeah, there's a little ambiguity here... `view` is the GUI view, where GUI callbacks are made.
    # `parent` is the parent view instance, which is a core instance.
    def __init__(self, view, parent_view):
        Listener.__init__(self, parent_view)
        HideableObject.__init__(self)
        self.view = view
        self.parent_view = parent_view
        self.mainwindow = parent_view.mainwindow
        self.document = self.mainwindow.document
        self.app = self.document.app
    
    def dispatch(self, msg):
        if self._hidden:
            self._process_message(msg)
        else:
            Listener.dispatch(self, msg)
    

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
    

class GUIPanel(DocumentGUIObject):
    def _load(self):
        raise NotImplementedError()
    
    def _new(self):
        raise NotImplementedError()
    
    def _save(self):
        raise NotImplementedError()
    
    def load(self):
        # If the panel can't load, OperationAborted will be raised. If a message to the user is
        # required, the OperationAborted exception will have a non-empty message
        self.view.pre_load()
        self._load()
        self.view.post_load()
    
    def new(self):
        # Same as in load()
        self.view.pre_load()
        self._new()
        self.view.post_load()
    
    def save(self):
        self.view.pre_save()
        self._save()
    

class MainWindowPanel(GUIPanel):
    def __init__(self, view, mainwindow):
        GUIPanel.__init__(self, view, mainwindow.document)
        self.mainwindow = mainwindow
    

class BaseView(Repeater, HideableObject, DocumentNotificationsMixin, MainWindowNotificationsMixin):
    VIEW_TYPE = -1
    
    def __init__(self, view, mainwindow):
        Repeater.__init__(self, mainwindow)
        HideableObject.__init__(self)
        self._children = []
        self.view = view
        self.mainwindow = mainwindow
        self.document = mainwindow.document
        self.app = mainwindow.document.app
    
    def dispatch(self, msg):
        if self._hidden:
            self._process_message(msg)
            self._repeat_message(msg)
        else:
            Repeater.dispatch(self, msg)
    
    # This has to be call *once* and *right after creation*. The children are set after
    # initialization so that we can pass a reference to self during children's initialization.
    def set_children(self, children):
        self._children = children
        for child in children:
            child.connect()
    
    def show(self):
        HideableObject.show(self)
        for child in self._children:
            child.show()
    
    def hide(self):
        HideableObject.hide(self)
        for child in self._children:
            child.hide()
    
