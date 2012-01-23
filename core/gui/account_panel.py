# Created By: Virgil Dupras
# Created On: 2008-07-03
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.currency import Currency
from hscommon.gui.selectable_list import GUISelectableList
from hscommon.trans import tr

from ..exception import DuplicateAccountNameError
from ..model.account import AccountType
from .base import MainWindowPanel, LinkedSelectableList

ACCOUNT_TYPE_DESC = {
    AccountType.Asset: tr("Asset"),
    AccountType.Liability: tr("Liability"),
    AccountType.Income: tr("Income"),
    AccountType.Expense: tr("Expense"),
}

class AccountTypeList(GUISelectableList):
    def __init__(self, panel):
        self.panel = panel
        account_types_desc = [ACCOUNT_TYPE_DESC[at] for at in AccountType.InOrder]
        GUISelectableList.__init__(self, account_types_desc)
    
    def _update_selection(self):
        GUISelectableList._update_selection(self)
        selected_type = AccountType.InOrder[self.selected_index]
        self.panel.type = selected_type

class AccountPanel(MainWindowPanel):
    def __init__(self, mainwindow):
        MainWindowPanel.__init__(self, mainwindow)
        self._init_fields()
        self.type_list = AccountTypeList(self)
        currencies_display = ['%s - %s' % (currency.code, currency.name) for currency in Currency.all]
        def setfunc(index):
            try:
                self.currency = Currency.all[index]
            except IndexError:
                pass
        self.currency_list = LinkedSelectableList(items=currencies_display, setfunc=setfunc)
    
    #--- Override
    def _load(self, account):
        self.document.stop_edition()
        self._init_fields()
        self.name = account.name
        self.type = account.type
        self.currency = account.currency
        self.account_number = account.account_number
        self.notes = account.notes
        self.type_list.select(AccountType.InOrder.index(self.type))
        self.currency_list.select(Currency.all.index(self.currency))
        self.can_change_currency = not any(e.reconciled for e in account.entries)
        self.account = account # for the save() assert
    
    def _save(self):
        kwargs = dict(name=self.name, type=self.type, account_number=self.account_number,
            notes=self.notes)
        if self.can_change_currency:
            kwargs['currency'] = self.currency
        try:
            self.document.change_accounts([self.account], **kwargs)
        except DuplicateAccountNameError:
            pass
    
    #--- Private
    def _init_fields(self):
        self.type = AccountType.Asset
        self.currency = None
        self.account_number = ''
    
