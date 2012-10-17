# Created By: Virgil Dupras
# Created On: 2008-09-04
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .base import ViewChild, MESSAGES_DOCUMENT_CHANGED

class Chart(ViewChild):
    #--- model --> view
    # draw_line(p1, p2, pen_id)
    # draw_rect(rect, pen_id, brush_id)
    # draw_pie(center, radius, start_angle, span_angle, brush_id)
    # draw_polygon(points, pen_id, brush_id)
    # draw_text(text, rect, font_id)
    # text_size(text, font_id) --> (width, height)
    #
    
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | {'accounts_excluded', 'date_range_changed'}
    
    def __init__(self, parent_view):
        ViewChild.__init__(self, parent_view)
        self.view_size = (0, 0)
    
    #--- Override
    def _revalidate(self):
        self.compute()
        self.view.refresh()
    
    #--- Virtual
    def compute(self):
        raise NotImplementedError()
    
    def draw(self):
        if self.has_view():
            self.draw_chart()
    
    #--- Public
    def set_view_size(self, width, height):
        # Some charts behave differently depending on what size they're given.
        self.view_size = (width, height)
    
    #--- Event Handlers
    def _data_changed(self):
        self._revalidate()
    
    account_changed = _data_changed
    account_deleted = _data_changed
    date_range_changed = _data_changed
    document_changed = _data_changed
    performed_undo_or_redo = _data_changed
    transaction_changed = _data_changed
    transaction_deleted = _data_changed
    transactions_imported = _data_changed
    
    #--- Properties
    @property
    def data(self):
        return self._data
    
    @property
    def title(self):
        return ''
    
    @property
    def currency(self):
        return self.document.default_currency
    
