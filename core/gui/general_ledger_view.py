# Created By: Virgil Dupras
# Created On: 2010-09-09
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from ..const import PaneType
from .base import BaseView, MESSAGES_DOCUMENT_CHANGED

class GeneralLedgerView(BaseView):
    VIEW_TYPE = PaneType.GeneralLedger
    PRINT_TITLE_FORMAT = tr('General Ledger from {start_date} to {end_date}')
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | {'filter_applied', 'date_range_changed',
        'transactions_selected'}
    
    def __init__(self, view, mainwindow):
        BaseView.__init__(self, view, mainwindow)
        self.bind_messages(self.INVALIDATING_MESSAGES, self._refresh_totals)
    
    #--- Overrides
    def set_children(self, children):
        [self.gltable] = children
        self.maintable = self.gltable
        BaseView.set_children(self, children)
    
    def _revalidate(self):
        self._refresh_totals()
    
    #--- Public
    def delete_item(self):
        self.gltable.delete()
    
    def edit_item(self):
        self.mainwindow.edit_selected_transactions()
    
    def new_item(self):
        self.gltable.add()
    
    #--- Private
    def _refresh_totals(self):
        selected, total, total_debit, total_credit = self.gltable.get_totals()
        total_debit_fmt = self.document.format_amount(total_debit)
        total_credit_fmt = self.document.format_amount(total_credit)
        msg = tr("{0} out of {1} selected. Debit: {2} Credit: {3}")
        self.status_line = msg.format(selected, total, total_debit_fmt, total_credit_fmt)
    
