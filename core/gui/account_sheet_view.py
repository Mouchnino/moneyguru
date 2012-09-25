# Created By: Virgil Dupras
# Created On: 2010-05-10
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .base import BaseView

class AccountSheetView(BaseView):
    INVALIDATING_MESSAGES = BaseView.INVALIDATING_MESSAGES | {'area_visibility_changed'}
    SAVENAME = ''
    
    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        self.bind_messages(self.INVALIDATING_MESSAGES, self._revalidate)
        # Set self.sheet, self.graph and self.pie in subclasses init
    
    #--- Overrides
    def _revalidate(self):
        BaseView._revalidate(self)
        self.view.update_visibility()
    
    def restore_subviews_size(self):
        if self.graph.view_size[1]:
            # Was already restored
            return
        prefname = '{}.GraphHeight'.format(self.SAVENAME)
        self.graph_height_to_restore = self.document.get_default(prefname, 0)
        prefname = '{}.PieWidth'.format(self.SAVENAME)
        self.pie_width_to_restore = self.document.get_default(prefname, 0)
    
    def save_preferences(self):
        self.sheet.save_preferences()
        height = self.graph.view_size[1]
        # It's possible that set_view_size() has never been called. In this case, we have (0, 0).
        if height: 
            prefname = '{}.GraphHeight'.format(self.SAVENAME)
            self.document.set_default(prefname, height)
        width = self.pie.view_size[0]
        if width:
            prefname = '{}.PieWidth'.format(self.SAVENAME)
            self.document.set_default(prefname, width)
    
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
    
