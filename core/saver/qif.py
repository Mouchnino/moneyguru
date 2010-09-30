# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..model.account import AccountType
from ..model.date import format_date

def save(filename, accounts):
    def format_amount_for_qif(amount):
        return '%1.2f' % amount.value if amount else '0.00'
    
    accounts = [a for a in accounts if a.is_balance_sheet_account()]
    txns_seen = set()
    lines = []
    for account in accounts:
        qif_account_type = 'Oth L' if account.type == AccountType.Liability else 'Bank'
        lines.append('!Account')
        lines.append('N%s' % account.name)
        lines.append('B%s' % format_amount_for_qif(account.entries.balance()))
        lines.append('T%s' % qif_account_type)
        lines.append('^')
        lines.append('!Type:%s' % qif_account_type)
        for entry in account.entries:
            if entry.transaction in txns_seen:
                continue
            txns_seen.add(entry.transaction)
            lines.append('D%s' % format_date(entry.date, 'MM/dd/yy'))
            lines.append('T%s' % format_amount_for_qif(entry.amount))
            if entry.description:
                lines.append('M%s' % entry.description)
            if entry.payee:
                lines.append('P%s' % entry.payee)
            if entry.checkno:
                lines.append('N%s' % entry.checkno)
            if len(entry.splits) > 1 or any(s.memo for s in entry.transaction.splits):
                for split in entry.splits:
                    if split.account is not None:
                        lines.append('S%s' % split.account.name)
                    if split.memo:
                        lines.append('E%s' % split.memo)
                    if split.reconciled:
                        lines.append('CR')
                    lines.append('$%s' % format_amount_for_qif(-split.amount))
            else:
                if entry.transfer:
                    lines.append('L%s' % entry.transfer[0].name)
                if entry.reconciled:
                    lines.append('CR')
            lines.append('^')
    fd = open(filename, 'wt', encoding='utf-8')
    fd.write('\n'.join(lines))
    fd.close()
