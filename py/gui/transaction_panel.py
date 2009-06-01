# Unit Name: moneyguru.gui.transaction_panel
# Created By: Virgil Dupras
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from calendar import monthrange
from datetime import date

from hsutil.notify import Broadcaster
from hsutil.misc import first

from ..const import (REPEAT_NEVER, REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY, 
    REPEAT_YEARLY, REPEAT_WEEKDAY, REPEAT_WEEKDAY_LAST)
from ..model.account import Account, INCOME, EXPENSE
from ..model.transaction import Split, Transaction
from .base import DocumentGUIObject
from .complete import TransactionCompletionMixIn

REPEAT_OPTIONS_ORDER = [REPEAT_NEVER, REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY, REPEAT_YEARLY, 
                        REPEAT_WEEKDAY, REPEAT_WEEKDAY_LAST]

class TransactionPanel(DocumentGUIObject, Broadcaster, TransactionCompletionMixIn):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        Broadcaster.__init__(self)
        self.transaction = Transaction(date.today())
        self._repeat_index = 0
        self._repeat_every = 1
        self.is_recurrent = False
    
    def can_load(self):
        return len(self.document.selected_transactions) == 1
    
    def load(self):
        self.document.stop_edition()
        original = self.document.selected_transaction
        assert original is not None            
        self.transaction = original.replicate(link_splits=True)
        self.original = original
        self.is_recurrent = hasattr(original, 'recurrence')
        if self.is_recurrent:
            repeat_option = original.recurrence.repeat_type
            self._repeat_index = REPEAT_OPTIONS_ORDER.index(repeat_option)
            self._repeat_every = original.recurrence.repeat_every
        else:
            self._repeat_index = 0
        self.view.refresh_mct_button()
        self.notify('panel_loaded')
    
    def save(self):
        repeat_option = REPEAT_OPTIONS_ORDER[self.repeat_index]
        self.document.change_transaction(self.original, self.transaction, repeat_option, self.repeat_every)
    
    def change_split(self, split, account_name, amount, memo):
        if account_name:
            account_type = split.account.type if split.account else EXPENSE if split.amount < 0 else INCOME
            split.account = Account(account_name, self.app.default_currency, account_type)
        else:
            split.account = None
        split.amount = amount
        split.memo = memo
        self.transaction.balance(split)
        self.view.refresh_mct_button()
        self.notify('split_changed')
    
    def delete_split(self, split):
        self.transaction.splits.remove(split)
        self.transaction.balance()
        self.view.refresh_mct_button()
    
    def mct_balance(self):
        """Balances the mct by using xchange rates. The currency of the new split is the currency of
        the currently selected split.
        """
        self.notify('edition_must_stop')
        split = first(self.document.selected_splits)
        new_split_currency = self.app.default_currency
        if split is not None and split.amount != 0:
            new_split_currency = split.amount.currency
        self.transaction.mct_balance(new_split_currency)
        self.notify('split_changed')
    
    def new_split(self):
        transaction = self.transaction
        split = Split(transaction, None, 0)
        transaction.splits.append(split)
        return split
    
    @property
    def can_do_mct_balance(self):
        return self.transaction.is_mct
    
    @property
    def date(self):
        return self.app.format_date(self.transaction.date)
    
    @date.setter
    def date(self, value):
        date = self.app.parse_date(value)
        if date == self.transaction.date:
            return
        self.transaction.date = date
        self.view.refresh_repeat_options()
    
    @property
    def description(self):
        return self.transaction.description
    
    @description.setter
    def description(self, value):
        self.transaction.description = value
    
    @property
    def payee(self):
        return self.transaction.payee
    
    @payee.setter
    def payee(self, value):
        self.transaction.payee = value
    
    @property
    def checkno(self):
        return self.transaction.checkno
    
    @checkno.setter
    def checkno(self, value):
        self.transaction.checkno = value
    
    @property
    def repeat_every(self):
        return self._repeat_every
    
    @repeat_every.setter
    def repeat_every(self, value):
        value = max(1, value)
        self._repeat_every = value
        self.view.refresh_repeat_every()
    
    @property
    def repeat_every_desc(self):
        desc = {1: 'day', 2: 'week', 3: 'month', 4: 'year'}.get(self._repeat_index)
        if desc and self._repeat_every > 1:
            desc += 's'
        return desc
    
    @property
    def repeat_options(self):
        result = ['Never', 'Daily', 'Weekly', 'Monthly', 'Yearly']
        date = self.transaction.date
        weekday_name = date.strftime('%A')
        week_no = (date.day - 1) // 7
        position = ['first', 'second', 'third', 'fourth', 'fifth'][week_no]
        result.append('Every %s %s of the month' % (position, weekday_name))
        _, days_in_month = monthrange(date.year, date.month)
        if days_in_month - date.day < 7:
            result.append('Every last %s of the month' % weekday_name)
        return result
    
    @property
    def repeat_index(self):
        return self._repeat_index
    
    @repeat_index.setter
    def repeat_index(self, value):
        if value == self._repeat_index:
            return
        self._repeat_index = value
        self.view.refresh_repeat_every()
    

