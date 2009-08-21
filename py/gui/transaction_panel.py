# Created By: Virgil Dupras
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from hsutil.notify import Broadcaster
from hsutil.misc import first

from ..model.account import Account, INCOME, EXPENSE
from ..model.transaction import Split, Transaction
from .base import GUIPanel
from .complete import TransactionCompletionMixIn

class PanelWithTransaction(GUIPanel, Broadcaster, TransactionCompletionMixIn):
    """Base class for panels working with a transaction"""
    def __init__(self, view, document):
        GUIPanel.__init__(self, view, document)
        Broadcaster.__init__(self)
        self.transaction = Transaction(date.today())
    
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
    
    def new_split(self):
        transaction = self.transaction
        split = Split(transaction, None, 0)
        transaction.splits.append(split)
        return split
    
    #--- Properties
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
    

class TransactionPanel(PanelWithTransaction):
    #--- Override
    def _load(self):
        self.document.stop_edition()
        original = self.document.selected_transaction
        assert original is not None            
        self.transaction = original.replicate(link_splits=True)
        self.original = original
        self.view.refresh_mct_button()
        self.notify('panel_loaded')
    
    def _save(self):
        self.document.change_transaction(self.original, self.transaction)
    
    #--- Public
    def can_load(self):
        return len(self.document.selected_transactions) == 1
    
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
    
