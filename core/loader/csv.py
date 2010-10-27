# Created By: Virgil Dupras
# Created On: 2009-01-18
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license



import csv
import logging
from datetime import datetime
from hsutil.misc import stripfalse

from ..exception import FileFormatError, FileLoadError
from ..trans import tr
from . import base

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

MERGABLE_FIELDS = {CsvField.Description, CsvField.Payee}

class Loader(base.Loader):
    FILE_ENCODING = 'latin-1'
    def __init__(self, default_currency):
        base.Loader.__init__(self, default_currency)
        self.columns = []
        self.lines = []
        self.dialect = None # last used dialect
        self.rawlines = [] # last prepared file
    
    #--- Private
    @staticmethod
    def _merge_columns(columns, lines):
        # For any columns that is there more than once, merge the data that goes with it
        for field in MERGABLE_FIELDS:
            indexes = [i for i, f in enumerate(columns) if f == field]
            if len(indexes) <= 1:
                continue
            for line_index, line in enumerate(lines):
                elems = [line[i] for i in indexes]
                merged_data = ' '.join(elems)
                new_line = line[:] # We don't want to touch original lines
                new_line[indexes[0]] = merged_data
                for index_to_remove in reversed(indexes[1:]):
                    del new_line[index_to_remove]
                lines[line_index] = new_line
            for index_to_remove in reversed(indexes[1:]):
                del columns[index_to_remove]
    
    def _prepare(self, infile):
        # Comment lines can confuse the sniffer. We remove them
        content = infile.read()
        content = content.replace('\0', '')
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
    
    def _scan_lines(self, encoding=None):
        rawlines = self.rawlines
        if encoding and encoding != self.FILE_ENCODING:
            # rawlines is a list of ustrings decoded using latin-1, so if we want to re-decode them
            # using another encoding, we have to re-encode them and the decode them using our encoding
            rawlines = (line.encode(self.FILE_ENCODING).decode(encoding) for line in rawlines)
        try:
            reader = csv.reader(iter(rawlines), self.dialect)
        except TypeError:
            logging.warning("Invalid Dialect (strangely...). Delimiter: %r", self.dialect.delimiter)
        lines = stripfalse(reader)
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
        lines = self.lines[:]
        colcount = len(lines[0]) if lines else 0
        columns = self.columns[:colcount]
        self._merge_columns(columns, lines)
        ci = {}
        for index, field in enumerate(columns):
            if field is not None:
                ci[field] = index
        hasdate = CsvField.Date in ci
        hasamount = (CsvField.Amount in ci) or (CsvField.Increase in ci and CsvField.Decrease in ci)
        if not (hasdate and hasamount):
            raise FileLoadError(tr("The Date and Amount columns must be set."))
        self.account_info.name = 'CSV Import'
        date_index = ci[CsvField.Date]
        lines_to_load = []
        for line in lines:
            line = line[:]
            cleaned_str_date = self.clean_date(line[date_index])
            if cleaned_str_date is None:
                logging.warning('{0} is not a date. Ignoring line'.format(line[date_index]))
            else:
                line[date_index] = cleaned_str_date
                lines_to_load.append(line)
        str_dates = [line[date_index] for line in lines_to_load]
        date_format = self.guess_date_format(str_dates)
        if date_format is None:
            raise FileLoadError(tr("The Date column has been set on a column that doesn't contain dates."))
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
                if isinstance(value, str):
                    value = value.strip()
                if value:
                    setattr(self.transaction_info, attr, value)
    
    #--- Public
    def rescan(self, encoding=None):
        self._scan_lines(encoding=encoding)
    
