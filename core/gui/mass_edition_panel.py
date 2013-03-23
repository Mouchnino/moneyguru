# Created By: Virgil Dupras
# Created On: 2008-07-25
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.currency import Currency
from hscommon.util import allsame, flatten
from hscommon.gui.text_field import TextField

from ..exception import OperationAborted
from .base import MainWindowPanel, LinkedSelectableList
from .completable_edit import CompletableEdit

class MassEditTextField(TextField):
    def __init__(self, panel, fieldname):
        TextField.__init__(self)
        self._panel = panel
        self._attrname = '_' + fieldname
        self._enabledname = fieldname + '_enabled'
    
    def _update(self, newvalue):
        setattr(self._panel, self._attrname, newvalue)
        setattr(self._panel, self._enabledname, True)
        self._panel.view.refresh()
    

class MassEditDateField(MassEditTextField):
    def _parse(self, text):
        return self._panel.app.parse_date(text)
    
    def _format(self, value):
        return self._panel.app.format_date(value)
    

class MassEditAmountField(MassEditTextField):
    def _parse(self, text):
        return self._panel.app.parse_amount(text)
    
    def _format(self, value):
        return self._panel.app.format_amount(value)
    
 
class MassEditionPanel(MainWindowPanel):
    def __init__(self, mainwindow):
        MainWindowPanel.__init__(self, mainwindow)
        self.date_field = MassEditDateField(self, 'date')
        self.description_field = MassEditTextField(self, 'description')
        self.payee_field = MassEditTextField(self, 'payee')
        self.checkno_field = MassEditTextField(self, 'checkno')
        self.from_field = MassEditTextField(self, 'from')
        self.to_field = MassEditTextField(self, 'to')
        self.amount_field = MassEditAmountField(self, 'amount')
        self.completable_edit = CompletableEdit(mainwindow)
        currencies_display = ['%s - %s' % (currency.code, currency.name) for currency in Currency.all]
        def setfunc(index):
            if 0 <= index < len(Currency.all):
                currency = Currency.all[index]
            else:
                currency = None
            if currency != self.currency:
                self.currency = currency
                self.currency_enabled = currency != None
                self.view.refresh()
        self.currency = None
        self.currency_list = LinkedSelectableList(items=currencies_display, setfunc=setfunc)
        self._init_checkboxes()
    
    #--- Private
    def _init_checkboxes(self):
        self.date_enabled = False
        self.description_enabled = False
        self.payee_enabled = False
        self.checkno_enabled = False
        self.from_enabled = False
        self.to_enabled = False
        self.amount_enabled = False
        self.currency_enabled = False
    
    #--- Override
    def _load(self):
        transactions = self.mainwindow.selected_transactions
        if len(transactions) < 2:
            raise OperationAborted()
        self.can_change_accounts = all(len(t.splits) == 2 for t in transactions)
        self.can_change_amount = all(t.can_set_amount for t in transactions)
        self.date_field.value = date.today()
        self.description_field.text = ''
        self.payee_field.text = ''
        self.checkno_field.text = ''
        self.from_field.text = ''
        self.to_field.text = ''
        self.amount_field.value = 0
        self.currency = None
        first = transactions[0]
        if allsame(t.date for t in transactions):
            self.date_field.value = first.date
        if allsame(t.description for t in transactions):
            self.description_field.text = first.description
        if allsame(t.payee for t in transactions):
            self.payee_field.text = first.payee
        if allsame(t.checkno for t in transactions):
            self.checkno_field.text = first.checkno
        splits = flatten(t.splits for t in transactions)
        splits = [s for s in splits if s.amount]
        if splits and allsame(s.amount.currency for s in splits):
            self.currency = splits[0].amount.currency
        else:
            self.currency = self.document.default_currency
        self.currency_list.select(Currency.all.index(self.currency))
        if self.can_change_accounts:
            def get_from(t):
                s1, s2 = t.splits
                return s1 if s1.amount <=0 else s2
        
            def get_to(t):
                s1, s2 = t.splits
                return s2 if s1.amount <=0 else s1
        
            def get_name(split):
                return split.account.name if split.account is not None else ''
        
            if allsame(get_name(get_from(t)) for t in transactions):
                self.from_field.text = get_name(get_from(first))
            if allsame(get_name(get_to(t)) for t in transactions):
                self.to_field.text = get_name(get_to(first))
        if self.can_change_amount:
            if allsame(t.amount for t in transactions):
                self.amount_field.value = first.amount
        self._init_checkboxes()
    
    def _save(self):
        transactions = self.mainwindow.selected_transactions
        kw = {}
        if self.date_enabled:
            kw['date'] = self.date_field.value
        if self.description_enabled:
            kw['description'] = self.description_field.text
        if self.payee_enabled:
            kw['payee'] = self.payee_field.text
        if self.checkno_enabled:
            kw['checkno'] = self.checkno_field.text
        if self.from_enabled:
            kw['from_'] = self.from_field.text
        if self.to_enabled:
            kw['to'] = self.to_field.text
        if self.amount_enabled:
            kw['amount'] = self.amount_field.value
        if self.currency_enabled:
            kw['currency'] = self.currency
        if kw:
            self.document.change_transactions(transactions, **kw)
    
