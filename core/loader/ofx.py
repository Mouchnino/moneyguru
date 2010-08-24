# coding=utf-8
# Created By: Eric Mc Sween
# Created On: 2008-02-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license
#
# Sections refer to the OFX 1.0.3 spec.

from datetime import datetime
from itertools import dropwhile
from sgmllib import SGMLParser

from ..exception import FileFormatError
from . import base

class Loader(SGMLParser, base.Loader):
    FILE_ENCODING = 'cp1252'
    def __init__(self, default_currency):
        SGMLParser.__init__(self)
        base.Loader.__init__(self, default_currency)
        self.data = ''
        self.data_handler = None
    
    #--- Override
    def _parse(self, infile):
        # First line is OFXHEADER (section 2.2.1)
        line = '\n'
        while line and not line.strip(): # skip the first lines if they're blank
            line = infile.readline()
        if line.strip() != 'OFXHEADER:100':
            raise FileFormatError()
        self.lines = list(infile)
    
    def _load(self):
        is_header = lambda line: not line.startswith('<')
        for line in dropwhile(is_header, self.lines):
            self.feed(line)
        self.close()
    
    #--- Helper methods

    def flush_data(self):
        if self.data_handler:
            self.data_handler(self.data.strip())
            self.data_handler = None
        self.data = ''
    
    #--- Global hooks

    def handle_starttag(self, tag, method, attributes):
        self.flush_data()
        SGMLParser.handle_starttag(self, tag, method, attributes)

    def handle_endtag(self, tag, method):
        self.flush_data()
        SGMLParser.handle_endtag(self, tag, method)

    def unknown_starttag(self, tag, attributes):
        self.flush_data()

    def unknown_endtag(self, tag):
        self.flush_data()

    def handle_data(self, data):
        self.data += data

    #--- Account tags

    def start_stmtrs(self, attributes):
        self.start_account()

    def end_stmtrs(self):
        a = self.account_info
        if hasattr(a, 'ofx_bank_id') and hasattr(a, 'ofx_acct_id'):
            ofx_branch_id = getattr(a, 'ofx_branch_id', '')
            a.reference = '|'.join([a.ofx_bank_id, ofx_branch_id, a.ofx_acct_id])
        self.flush_account()
    
    def start_curdef(self, attributes):
        self.data_handler = self.handle_curdef

    def handle_curdef(self, data):
        self.account_info.currency = data
    
    def start_bankid(self, attributes):
        self.data_handler = self.handle_bankid

    def handle_bankid(self, data):
        self.account_info.ofx_bank_id = data

    def start_branchid(self, attributes):
        self.data_handler = self.handle_branchid

    def handle_branchid(self, data):
        self.account_info.ofx_branch_id = data

    def start_acctid(self, attributes):
        self.data_handler = self.handle_acctid

    def handle_acctid(self, data):
        self.account_info.ofx_acct_id = data
        self.account_info.name = data
    
    def start_balamt(self, attributes):
        self.data_handler = self.handle_balamt

    def handle_balamt(self, data):
        self.account_info.balance = data

    #--- Entry tags

    def start_stmttrn(self, attributes):
        self.start_transaction()

    def end_stmttrn(self):
        self.flush_transaction()
        
    def start_fitid(self, attributes):
        self.data_handler = self.handle_fitid

    def handle_fitid(self, data):
        self.transaction_info.reference = data

    def start_name(self, attributes):
        self.data_handler = self.handle_name
    
    def handle_name(self, data):
        self.transaction_info.description = data

    def start_dtposted(self, attributes):
        self.data_handler = self.handle_dtposted

    def handle_dtposted(self, data):
        self.transaction_info.date = datetime.strptime(data[:8], '%Y%m%d').date()

    def start_trnamt(self, attributes):
        self.data_handler = self.handle_trnamt

    def handle_trnamt(self, data):
        self.transaction_info.amount = data
