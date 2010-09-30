# Created By: Virgil Dupras
# Created On: 2008-07-03
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.currency import Currency

from ..exception import DuplicateAccountNameError, OperationAborted
from ..model.account import AccountType
from .base import MainWindowPanel

class AccountPanel(MainWindowPanel):
    def __init__(self, view, mainwindow):
        MainWindowPanel.__init__(self, view, mainwindow)
        self._init_fields()
    
    #--- Override
    def _load(self, account):
        self.document.stop_edition()
        self._init_fields()
        self.name = account.name
        self.type = account.type
        self.currency = account.currency
        self.account_number = account.account_number
        self.notes = account.notes
        self.type_index = AccountType.InOrder.index(self.type)
        self.currency_index = Currency.all.index(self.currency)
        self.account = account # for the save() assert
    
    def _save(self):
        try:
            self.document.change_account(self.account, name=self.name, type=self.type, 
                currency=self.currency, account_number=self.account_number, notes=self.notes)
        except DuplicateAccountNameError:
            pass
    
    #--- Private
    def _init_fields(self):
        self.type = AccountType.Asset
        self._type_index = 0
        self.currency = None
        self.account_number = ''
    
    #--- Properties
    @property
    def currency_index(self):
        return self._currency_index
    
    @currency_index.setter
    def currency_index(self, index):
        try:
            self.currency = Currency.all[index]
        except IndexError:
            pass
        else:
            self._currency_index = index
    
    @property
    def type_index(self):
        return self._type_index
    
    @type_index.setter
    def type_index(self, index):
        try:
            self.type = AccountType.InOrder[index]
        except IndexError:
            pass
        else:
            self._type_index = index
    
