# Created By: Virgil Dupras
# Created On: 2009-01-18
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import absolute_import

import csv
import logging
from datetime import datetime

from . import base
from ..exception import FileFormatError, FileLoadError

class CsvField(object):
    Date = 'date'
    Description = 'description'
    Payee = 'payee'
    Checkno = 'checkno'
    Transfer = 'transfer'
    Amount = 'amount'
    Increase = 'increase'
    Decrease = 'decrease'
    Currency = 'currency'
    Reference = 'reference'

class Loader(base.Loader):
    FILE_OPEN_MODE = 'U' # universal line-ends. Deals with \r and \n
    def __init__(self, default_currency):
        base.Loader.__init__(self, default_currency)
        self.column_indexes = {}
        self.lines = []
        self.dialect = None # last used dialect
        self.rawlines = [] # last prepared file
    
    #--- Private
    def _prepare(self, infile):
        # Comment lines can confuse the sniffer. We remove them
        content = infile.read()
        lines = content.split('\n')
        stripped_lines = [line.strip() for line in lines]
        stripped_lines = [line for line in lines if line and not line.startswith('#')]
        try:
            self.dialect = csv.Sniffer().sniff('\n'.join(stripped_lines))
        except csv.Error:
            # sometimes, it's the footer that plays trick with the sniffer. Let's try again, with
            # the last line removed
            try:
                self.dialect = csv.Sniffer().sniff('\n'.join(stripped_lines[:-1]))
            except csv.Error:
                raise FileFormatError()
        self.rawlines = lines
    
    def _scan_lines(self):
        def decode_line(line):
            return [unicode(cell, 'latin-1') for cell in line]
        
        try:
            reader = csv.reader(iter(self.rawlines), self.dialect)
        except TypeError:
            logging.warning(u"Invalid Dialect (strangely...). Delimiter: %r", self.dialect.delimiter)
        lines = [decode_line(line) for line in reader if line]
        # complete smaller lines and strip whitespaces
        maxlen = max(len(line) for line in lines)
        for line in (l for l in lines if len(l) < maxlen):
            line += [''] * (maxlen - len(line))
        self.lines = lines
    
    #--- Override
    def _parse(self, infile):
        self._prepare(infile)
        self._scan_lines()
    
    def _load(self):
        ci = self.column_indexes
        colcount = len(self.lines[0]) if self.lines else 0
        ci = dict((attr, index) for attr, index in ci.iteritems() if index < colcount)
        hasdate = CsvField.Date in ci
        hasamount = (CsvField.Amount in ci) or (CsvField.Increase in ci and CsvField.Decrease in ci)
        if not (hasdate and hasamount):
            raise FileLoadError('The Date and Amount columns must be set')
        self.account_info.name = 'CSV Import'
        date_index = ci[CsvField.Date]
        lines_to_load = []
        for line in self.lines:
            line = line[:]
            cleaned_str_date = self.clean_date(line[date_index])
            if cleaned_str_date is None:
                logging.warning(u'{0} is not a date. Ignoring line'.format(line[date_index]))
            else:
                line[date_index] = cleaned_str_date
                lines_to_load.append(line)
        str_dates = [line[date_index] for line in lines_to_load]
        date_format = self.guess_date_format(str_dates)
        if date_format is None:
            raise FileLoadError('The Date column has been set on a column that doesn\'t contain dates')
        for line in lines_to_load:
            self.start_transaction()
            for attr, index in ci.items():
                value = line[index]
                if attr == CsvField.Date:
                    value = datetime.strptime(value, date_format).date()
                elif attr == CsvField.Increase:
                    attr = CsvField.Amount
                elif attr == CsvField.Decrease:
                    attr = CsvField.Amount
                    if value.strip() and not value.startswith('-'):
                        value = '-' + value
                if isinstance(value, basestring):
                    value = value.strip()
                if value:
                    setattr(self.transaction_info, attr, value)
    
    #--- Public
    def rescan(self):
        self._scan_lines()
    
