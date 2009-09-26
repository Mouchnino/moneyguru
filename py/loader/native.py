# Created By: Virgil Dupras
# Created On: 2008-02-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import datetime
import xml.etree.cElementTree as ET

from hsutil.misc import tryint

from ..exception import FileFormatError
from ..model.amount import parse_amount
from .base import SplitInfo, TransactionInfo
from . import base

class Loader(base.Loader):
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
                return datetime.strptime(s, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return default
        
        def read_transaction_element(element, info):
            attrib = element.attrib
            info.account = attrib.get('account')
            info.date = str2date(attrib.get('date'), TODAY)
            info.description = attrib.get('description')
            info.payee = attrib.get('payee')
            info.checkno = attrib.get('checkno')
            info.transfer = attrib.get('transfer')
            try:
                info.mtime = int(attrib.get('mtime', 0))
            except ValueError:
                info.mtime = 0
            info.reference = attrib.get('reference')
            for split_element in element.getiterator('split'):
                attrib = split_element.attrib
                split_info = SplitInfo()
                split_info.account = split_element.attrib.get('account')
                split_info.amount = split_element.attrib.get('amount')
                split_info.memo = split_element.attrib.get('memo')
                split_info.reference = split_element.attrib.get('reference')
                split_info.reconciled = split_element.attrib.get('reconciled') == 'y'
                info.splits.append(split_info)
            return info
        
        root = self.root
        for group_element in root.getiterator('group'):
            self.start_group()
            attrib = group_element.attrib
            self.group_info.name = attrib.get('name')
            self.group_info.type = attrib.get('type')
            self.flush_group()
        for account_element in root.getiterator('account'):
            self.start_account()
            attrib = account_element.attrib
            self.account_info.name = attrib.get('name')
            self.account_info.currency = attrib.get('currency')
            self.account_info.type = attrib.get('type')
            self.account_info.group = attrib.get('group')
            self.account_info.budget = attrib.get('budget')
            self.account_info.budget_target = attrib.get('budget_target')
            self.account_info.reference = attrib.get('reference')
            self.flush_account()
        elements = [e for e in root if e.tag == 'transaction'] # we only want transaction element *at the root*
        for transaction_element in elements:
            self.start_transaction()
            read_transaction_element(transaction_element, self.transaction_info)
            self.flush_transaction()
        for recurrence_element in root.getiterator('recurrence'):
            attrib = recurrence_element.attrib
            self.recurrence_info.repeat_type = attrib.get('type')
            self.recurrence_info.repeat_every = int(attrib.get('every', '1'))
            self.recurrence_info.stop_date = str2date(attrib.get('stop_date'))
            read_transaction_element(recurrence_element.find('transaction'), self.recurrence_info.transaction_info)
            for exception_element in recurrence_element.getiterator('exception'):
                try:
                    date = str2date(exception_element.attrib['date'])
                    txn_element = exception_element.find('transaction')
                    txn = read_transaction_element(txn_element, TransactionInfo()) if txn_element is not None else None
                    self.recurrence_info.date2exception[date] = txn
                except KeyError:
                    continue
            for change_element in recurrence_element.getiterator('change'):
                try:
                    date = str2date(change_element.attrib['date'])
                    txn_element = change_element.find('transaction')
                    txn = read_transaction_element(txn_element, TransactionInfo()) if txn_element is not None else None
                    self.recurrence_info.date2globalchange[date] = txn
                except KeyError:
                    continue
            self.flush_recurrence()
        for budget_element in root.getiterator('budget'):
            attrib = budget_element.attrib
            self.budget_info.account = attrib.get('account')
            self.budget_info.repeat_type = attrib.get('type')
            self.budget_info.repeat_every = tryint(attrib.get('every'), default=None)
            self.budget_info.target = attrib.get('target')
            self.budget_info.amount = attrib.get('amount')
            self.budget_info.start_date = str2date(attrib.get('start_date'))
            self.budget_info.stop_date = str2date(attrib.get('stop_date'))
            self.flush_budget()
    
    @staticmethod
    def parse_amount(string, currency): # uses with_expression=False for faster loading
        return parse_amount(string, currency, with_expression=False)
