# Created By: Virgil Dupras
# Created On: 2010-10-26
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import csv

from ..model.amount import format_amount
from ..model.date import format_date

def save(filename, accounts, daterange=None):
    fp = open(filename, 'wt', encoding='utf-8')
    writer = csv.writer(fp, delimiter=';', quotechar='"')
    HEADER = ['Account', 'Date', 'Description', 'Payee', 'Check #', 'Transfer', 'Amount', 'Currency']
    writer.writerow(HEADER)
    for account in accounts:
        entries = account.entries
        if daterange is not None:
            entries = [e for e in entries if e.date in daterange]
        for entry in entries:
            date_str = format_date(entry.date, 'dd/MM/yyyy')
            transfer = ', '.join(a.name for a in entry.transfer)
            amount = entry.amount
            if amount:
                amount_fmt = format_amount(amount, amount.currency)
                currency_code = amount.currency.code
            else:
                amount_fmt = '0.00'
                currency_code = ''
            row = [account.name, date_str, entry.description, entry.payee, entry.checkno, transfer,
                amount_fmt, currency_code]
            writer.writerow(row)
    fp.close()
