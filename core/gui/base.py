# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.notify import Listener, Repeater
from hscommon.gui.base import GUIObject
from hscommon.gui.selectable_list import GUISelectableList

from .print_view import PrintView

class DocumentNotificationsMixin:
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
    
    def document_restoring_preferences(self):
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
    

class MainWindowNotificationsMixin:
    def transactions_selected(self):
        pass
    
    def area_visibility_changed(self):
        pass
    

class SheetViewNotificationsMixin:
    def group_expanded_state_changed(self):
        pass
    

MESSAGES_EVERYTHING_CHANGED = {'document_changed', 'performed_undo_or_redo'}
MESSAGES_DOCUMENT_CHANGED = MESSAGES_EVERYTHING_CHANGED | {'account_added', 'account_changed',
    'account_deleted', 'transaction_changed', 'transaction_deleted', 'transactions_imported',
    'budget_changed', 'budget_deleted', 'schedule_changed', 'schedule_deleted'}

class HideableObject:
    # Messages that invalidates the view if received while it's hidden (its cache will be
    # revalidated upon show)
    INVALIDATING_MESSAGES = set()
    # Messages that are always passed, even if the object is hidden.
    ALWAYSON_MESSAGES = {'document_restoring_preferences'}
    
    def __init__(self):
        self._hidden = True
        self._invalidated = True
    
    #--- Protected
    def _process_message(self, msg):
        # Returns True if the message must be dispatched, False if not.
        if self._hidden and (msg in self.INVALIDATING_MESSAGES):
            self._invalidated = True
        return (not self._hidden) or (msg in self.ALWAYSON_MESSAGES)
    
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
    

class DocumentGUIObject(Listener, GUIObject, DocumentNotificationsMixin):
    def __init__(self, document):
        Listener.__init__(self, document)
        GUIObject.__init__(self)
        self.document = document
        self.app = document.app
    

class ViewChild(Listener, GUIObject, HideableObject, DocumentNotificationsMixin, MainWindowNotificationsMixin):
    def __init__(self, parent_view):
        Listener.__init__(self, parent_view)
        GUIObject.__init__(self)
        HideableObject.__init__(self)
        self.parent_view = parent_view
        self.mainwindow = parent_view.mainwindow
        self.document = self.mainwindow.document
        self.app = self.document.app
    
    def _process_message(self, msg):
        # We never want to process messages (such as document_restoring_preferences) when our view
        # is None because it will cause a crash.
        if self.view is None:
            return False
        else:
            return HideableObject._process_message(self, msg)
    
    def dispatch(self, msg):
        if self._process_message(msg):
            Listener.dispatch(self, msg)
    

class RestorableChild(ViewChild):
    def __init__(self, parent_view):
        ViewChild.__init__(self, parent_view)
        self._was_restored = False
    
    def _do_restore_view(self):
        # Virtual. Override this and perform actual restore process. Return True if restoration
        # could be done and False otherwise (for example, if our doc doesn't have a document ID yet
        # or other stuff like that).
        return False
    
    def restore_view(self):
        if not self._was_restored:
            if self._do_restore_view():
                self._was_restored = True
    

class GUIPanel(GUIObject):
    def __init__(self, document):
        GUIObject.__init__(self)
        self.document = document
        self.app = document.app
    
    #--- Virtual
    def _load(self):
        raise NotImplementedError()
    
    def _new(self):
        raise NotImplementedError()
    
    def _save(self):
        raise NotImplementedError()
    
    #--- Overrides
    def load(self, *args, **kwargs):
        # If the panel can't load, OperationAborted will be raised. If a message to the user is
        # required, the OperationAborted exception will have a non-empty message
        self.view.pre_load()
        self._load(*args, **kwargs)
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
    def __init__(self, mainwindow):
        GUIPanel.__init__(self, mainwindow.document)
        self.mainwindow = mainwindow
    

def _raise_notimplemented(self):
    raise NotImplementedError()
    
class BaseView(Repeater, GUIObject, HideableObject, DocumentNotificationsMixin, MainWindowNotificationsMixin):
    #--- model -> view calls:
    # restore_subviews_size()
    #
    
    VIEW_TYPE = -1
    PRINT_VIEW_CLASS = PrintView
    
    def __init__(self, mainwindow):
        Repeater.__init__(self, mainwindow)
        GUIObject.__init__(self)
        HideableObject.__init__(self)
        self._children = []
        self.mainwindow = mainwindow
        self.document = mainwindow.document
        self.app = mainwindow.document.app
        self._status_line = ""
    
    #--- Virtual
    new_item = _raise_notimplemented
    edit_item = _raise_notimplemented
    delete_item = _raise_notimplemented
    duplicate_item = _raise_notimplemented
    new_group = _raise_notimplemented
    navigate_back = _raise_notimplemented
    move_up = _raise_notimplemented
    move_down = _raise_notimplemented
    
    #--- Overrides
    def dispatch(self, msg):
        if self._process_message(msg):
            Repeater.dispatch(self, msg)
        else:
            self._repeat_message(msg)
    
    # This has to be call *once* and *right after creation*. The children are set after
    # initialization so that we can pass a reference to self during children's initialization.
    def set_children(self, children):
        self._children = children
        for child in children:
            child.connect()
        self.restore_subviews_size()
    
    def show(self):
        HideableObject.show(self)
        for child in self._children:
            child.show()
    
    def hide(self):
        HideableObject.hide(self)
        for child in self._children:
            child.hide()
    
    #--- Public
    @classmethod
    def can_perform(cls, action_name):
        # Base views have a specific set of actions they can perform, and the way they perform these
        # actions is defined by the subclasses. However, not all views can perform all actions.
        # You can use this method to determine whether a view can perform an action. It does so by
        # comparing the method of the view with our base method which we know is abstract and if
        # it's not the same, we know that the method was overridden and that we can perform the
        # action.
        mymethod = getattr(cls, action_name, None)
        assert mymethod is not None
        return mymethod is not getattr(BaseView, action_name, None)
    
    def restore_subviews_size(self):
        pass # Virtual
    
    def save_preferences(self):
        pass # Virtual
    
    #--- Properties
    @property
    def status_line(self):
        return self._status_line
    
    @status_line.setter
    def status_line(self, value):
        self._status_line = value
        if not self._hidden:
            self.mainwindow.update_status_line()
    
    #--- Notifications
    def document_restoring_preferences(self):
        self.restore_subviews_size()
        if self.view: # Some BaseView don't have a view
            self.view.restore_subviews_size()
    

class LinkedSelectableList(GUISelectableList):
    def __init__(self,  items=None, setfunc=None):
        # setfunc(newindex)
        GUISelectableList.__init__(self, items=items)
        self.setfunc = setfunc
    
    def _update_selection(self):
        GUISelectableList._update_selection(self)
        if self.setfunc is not None:
            self.setfunc(self.selected_index)
