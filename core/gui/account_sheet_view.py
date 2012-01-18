# Created By: Virgil Dupras
# Created On: 2010-05-10
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .base import BaseView

class AccountSheetView(BaseView):
    INVALIDATING_MESSAGES = BaseView.INVALIDATING_MESSAGES | {'area_visibility_changed'}
    
    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        self.bind_messages(self.INVALIDATING_MESSAGES, self._revalidate)
    
    # subclasses of this class must put their sheet gui element first in the children list
    def set_children(self, children):
        BaseView.set_children(self, children)
        self.sheet = children[0]
    
    #--- Overrides
    def _revalidate(self):
        BaseView._revalidate(self)
        self.view.update_visibility()
    
    #--- Public
    def collapse_group(self, group):
        group.expanded = False
        self.notify('group_expanded_state_changed')
    
    def delete_item(self):
        self.sheet.delete()
    
    def edit_item(self):
        selected_account = self.sheet.selected_account
        if selected_account is not None:
            self.mainwindow.account_panel.load(selected_account)
    
    def expand_group(self, group):
        group.expanded = True
        self.notify('group_expanded_state_changed')
    
    def new_item(self):
        self.sheet.add_account()
    
    def new_group(self):
        self.sheet.add_account_group()
    
    def show_account(self):
        self.sheet.show_selected_account()
    
