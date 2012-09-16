# Created By: Virgil Dupras
# Created On: 2008-02-15
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import datetime
import xml.etree.cElementTree as ET

from hscommon.currency import Currency
from hscommon.util import tryint

from ..exception import FileFormatError
from .base import SplitInfo, TransactionInfo
from . import base

class Loader(base.Loader):
    FILE_OPEN_MODE = 'rb'
    NATIVE_DATE_FORMAT = '%Y-%m-%d'
    
    def _parse(self, infile):
        try:
            root = ET.parse(infile).getroot()
        except SyntaxError:
            raise FileFormatError()
        if root.tag != 'moneyguru-file':
            raise FileFormatError()
        self.root = root
    
    def _load(self):
        TODAY = datetime.now().date()
        def str2date(s, default=None):
            try:
                return self.parse_date_str(s)
            except (ValueError, TypeError):
                return default
        
        def handle_newlines(s):
            # etree doesn't correctly save newlines. During save, we escape them. Now's the time to
            # restore them.
            # XXX After a while, when most users will have used a moneyGuru version that doesn't
            # need newline escaping on save, we can remove this one as well.
            if not s:
                return s
            return s.replace('\\n', '\n')
        
        def read_transaction_element(element, info):
            attrib = element.attrib
            info.account = attrib.get('account')
            info.date = str2date(attrib.get('date'), TODAY)
            info.description = attrib.get('description')
            info.payee = attrib.get('payee')
            info.checkno = attrib.get('checkno')
            info.notes = handle_newlines(attrib.get('notes'))
            info.transfer = attrib.get('transfer')
            try:
                info.mtime = int(attrib.get('mtime', 0))
            except ValueError:
                info.mtime = 0
            info.reference = attrib.get('reference')
            for split_element in element.iter('split'):
                attrib = split_element.attrib
                split_info = SplitInfo()
                split_info.account = split_element.attrib.get('account')
                split_info.amount = split_element.attrib.get('amount')
                split_info.memo = split_element.attrib.get('memo')
                split_info.reference = split_element.attrib.get('reference')
                if 'reconciled' in split_element.attrib: # legacy
                    split_info.reconciled = split_element.attrib['reconciled'] == 'y'
                if 'reconciliation_date' in split_element.attrib:
                    split_info.reconciliation_date = str2date(split_element.attrib['reconciliation_date'])
                info.splits.append(split_info)
            return info
        
        root = self.root
        self.document_id = root.attrib.get('document_id')
        props_element = root.find('properties')
        if props_element is not None:
            for name, value in props_element.attrib.items():
                # For now, all our prefs are ints, so we can simply assume tryint, but we'll
                # eventually need something more sophisticated.
                if name == 'default_currency':
                    value = Currency.by_code.get(value)
                else:
                    value = tryint(value, default=None)
                if name and value is not None:
                    self.properties[name] = value
        for group_element in root.iter('group'):
            self.start_group()
            attrib = group_element.attrib
            self.group_info.name = attrib.get('name')
            self.group_info.type = attrib.get('type')
            self.flush_group()
        for account_element in root.iter('account'):
            self.start_account()
            attrib = account_element.attrib
            self.account_info.name = attrib.get('name')
            self.account_info.currency = attrib.get('currency')
            self.account_info.type = attrib.get('type')
            self.account_info.group = attrib.get('group')
            self.account_info.budget = attrib.get('budget')
            self.account_info.budget_target = attrib.get('budget_target')
            self.account_info.reference = attrib.get('reference')
            self.account_info.account_number = attrib.get('account_number', '')
            self.account_info.notes = handle_newlines(attrib.get('notes', ''))
            self.flush_account()
        elements = [e for e in root if e.tag == 'transaction'] # we only want transaction element *at the root*
        for transaction_element in elements:
            self.start_transaction()
            read_transaction_element(transaction_element, self.transaction_info)
            self.flush_transaction()
        for recurrence_element in root.iter('recurrence'):
            attrib = recurrence_element.attrib
            self.recurrence_info.repeat_type = attrib.get('type')
            self.recurrence_info.repeat_every = int(attrib.get('every', '1'))
            self.recurrence_info.stop_date = str2date(attrib.get('stop_date'))
            read_transaction_element(recurrence_element.find('transaction'), self.recurrence_info.transaction_info)
            for exception_element in recurrence_element.iter('exception'):
                try:
                    date = str2date(exception_element.attrib['date'])
                    txn_element = exception_element.find('transaction')
                    txn = read_transaction_element(txn_element, TransactionInfo()) if txn_element is not None else None
                    self.recurrence_info.date2exception[date] = txn
                except KeyError:
                    continue
            for change_element in recurrence_element.iter('change'):
                try:
                    date = str2date(change_element.attrib['date'])
                    txn_element = change_element.find('transaction')
                    txn = read_transaction_element(txn_element, TransactionInfo()) if txn_element is not None else None
                    self.recurrence_info.date2globalchange[date] = txn
                except KeyError:
                    continue
            self.flush_recurrence()
        for budget_element in root.iter('budget'):
            attrib = budget_element.attrib
            self.budget_info.account = attrib.get('account')
            self.budget_info.repeat_type = attrib.get('type')
            self.budget_info.repeat_every = tryint(attrib.get('every'), default=None)
            self.budget_info.target = attrib.get('target')
            self.budget_info.amount = attrib.get('amount')
            self.budget_info.notes = attrib.get('notes')
            self.budget_info.start_date = str2date(attrib.get('start_date'))
            self.budget_info.stop_date = str2date(attrib.get('stop_date'))
            self.flush_budget()
    
