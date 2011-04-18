# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.notify import Broadcaster
from hscommon.util import first

from ..exception import OperationAborted
from ..model.account import Account, AccountType
from ..model.transaction import Split, Transaction
from .base import MainWindowPanel

class PanelWithTransaction(MainWindowPanel, Broadcaster):
    """Base class for panels working with a transaction"""
    def __init__(self, view, mainwindow):
        MainWindowPanel.__init__(self, view, mainwindow)
        Broadcaster.__init__(self)
        self.transaction = Transaction(date.today())
        self._selected_splits = []
    
    def change_split(self, split, account_name, amount, memo):
        if account_name:
            if split.account:
                account_type = split.account.type
            else:
                account_type = AccountType.Expense if split.amount < 0 else AccountType.Income
            split.account = Account(account_name, self.app.default_currency, account_type)
        else:
            split.account = None
        split.amount = amount
        split.memo = memo
        if split not in self.transaction.splits:
            self.transaction.splits.append(split)
        self.transaction.balance(split)
        self.notify('split_changed')
        self.view.refresh_for_multi_currency()
    
    def delete_split(self, split):
        split.remove()
        self.view.refresh_for_multi_currency()
    
    def new_split(self):
        return Split(self.transaction, None, 0)
    
    def select_splits(self, splits):
        self._selected_splits = splits
    
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
    
    @property
    def notes(self):
        return self.transaction.notes
    
    @notes.setter
    def notes(self, value):
        self.transaction.notes = value
    
    @property
    def is_multi_currency(self):
        return self.transaction.is_mct
    

class TransactionPanel(PanelWithTransaction):
    #--- Override
    def _load(self):
        if not self.mainwindow.selected_transactions:
            raise OperationAborted()
        original = self.mainwindow.selected_transactions[0]
        self.document.stop_edition()
        self.transaction = original.replicate()
        self.original = original
        self.view.refresh_for_multi_currency()
        self.notify('panel_loaded')
    
    def _save(self):
        self.document.change_transaction(self.original, self.transaction)
    
    #--- Public
    def mct_balance(self):
        """Balances the mct by using xchange rates. The currency of the new split is the currency of
        the currently selected split.
        """
        self.notify('edition_must_stop')
        split = first(self._selected_splits)
        new_split_currency = self.app.default_currency
        if split is not None and split.amount != 0:
            new_split_currency = split.amount.currency
        self.transaction.mct_balance(new_split_currency)
        self.notify('split_changed')
    
    @property
    def date(self):
        return self.app.format_date(self.transaction.date)
    
    @date.setter
    def date(self, value):
        self.transaction.date = self.app.parse_date(value)
    
