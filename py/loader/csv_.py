# Unit Name: moneyguru.loader.csv_
# Created By: Virgil Dupras
# Created On: 2009-01-18
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# The csv_ name is because when trying to import the csv from python's stdlib, all hell breaks
# loose, *even* with absolute_import

import csv
import logging
from datetime import datetime

from . import base
from ..exception import FileFormatError, FileLoadError

CSV_DATE = 'date'
CSV_DESCRIPTION = 'description'
CSV_PAYEE = 'payee'
CSV_CHECKNO = 'checkno'
CSV_TRANSFER = 'transfer'
CSV_AMOUNT = 'amount'
CSV_CURRENCY = 'currency'
CSV_REFERENCE = 'reference'

class Loader(base.Loader):
    def __init__(self, default_currency):
        base.Loader.__init__(self, default_currency)
        self.column_indexes = {}
        self.lines = []
    
    #--- Override
    def _parse(self, infile):
        def decode_line(line):
            return [unicode(cell, 'latin-1') for cell in line]
        
        # Comment lines can confuse the sniffer. We remove them
        content = infile.read()
        lines = content.split('\n')
        stripped_lines = [line for line in lines if not line.strip().startswith('#')]
        content = '\n'.join(stripped_lines)
        try:
            dialect = csv.Sniffer().sniff(content)
        except csv.Error:
            raise FileFormatError()
        infile.seek(0)
        reader = csv.reader(infile, dialect)
        lines = [decode_line(line) for line in reader if line]
        # complete smaller lines and strip whitespaces
        maxlen = max(len(line) for line in lines)
        for line in (l for l in lines if len(l) < maxlen):
            line += [''] * (maxlen - len(line))
        self.lines = lines
    
    def _load(self):
        if not (CSV_DATE in self.column_indexes and CSV_AMOUNT in self.column_indexes):
            raise FileLoadError('The Date and Amount columns must be set')
        self.account_info.name = 'CSV Import'
        date_index = self.column_indexes[CSV_DATE]
        for line in self.lines:
            cleaned_str_date = self.clean_date(line[date_index])
            if cleaned_str_date is None:
                logging.warning(u'{0} is not a date. Ignoring line'.format(line[date_index]))
            line[date_index] = cleaned_str_date
        self.lines = [line for line in self.lines if line[date_index] is not None]
        str_dates = [line[date_index] for line in self.lines]
        date_format = self.guess_date_format(str_dates)
        if date_format is None:
            raise FileLoadError('The Date column has been set on a column that doesn\'t contain dates')
        for line in self.lines:
            self.start_transaction()
            for attr, index in self.column_indexes.items():
                value = line[index]
                if attr == CSV_DATE:
                    value = datetime.strptime(value, date_format).date()
                elif isinstance(value, basestring):
                    value = value.strip()
                setattr(self.transaction_info, attr, value)
    