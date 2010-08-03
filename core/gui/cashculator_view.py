# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-08-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# NOTE: The cashculator integration code has no automated tests. Developing it is so much try/error
# and the wanted database values are so much subject to change that I found maintaining tests
# beside it counter-productive. Therefore, be careful when modifying this code, there's no safety net.

from datetime import date

from hsutil import io
from hsutil.path import Path
from hscommon.cocoa.objcmin import (NSSearchPathForDirectoriesInDomains, NSApplicationSupportDirectory,
    NSUserDomainMask)

from ..const import PaneType
from ..model.account import AccountType
from ..model.cashculator import CashculatorDB
from ..model.date import MonthRange
from .base import BaseView

MONTHS_TO_FILL = 4

class CashculatorView(BaseView):
    VIEW_TYPE = PaneType.Cashculator
    
    def __init__(self, view, mainwindow):
        BaseView.__init__(self, view, mainwindow)
        self._db = None
    
    def set_children(self, children):
        BaseView.set_children(self, children)
        [self.atable] = children
    
    #--- Private
    def _open_db(self):
        # If there's no CC db in moneyGuru's appdata folder, copy a model from CC's appdata,
        # and re-initialize it.
        appsupport = Path(NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,
            NSUserDomainMask, True)[0])
        mgccpath = appsupport + 'moneyGuru/cc'
        mgccdb = mgccpath + 'CCDB'
        if not io.exists(mgccdb):
            ccpath = appsupport + 'cashculator'
            ccdb = ccpath + 'CCDB'
            if not io.exists(mgccpath):
                io.makedirs(mgccpath)
            io.copy(ccdb, mgccdb)
        self._db = CashculatorDB(unicode(mgccdb))
    
    #--- Public
    def get_db(self):
        if self._db is None:
            self._open_db()
        return self._db
    
    def update_db(self):
        db = self.get_db()
        # Update CC db with actual data from moneyGuru.
        accounts = [row.account for row in self.atable]
        accountnames = set(a.name for a in accounts)
        categories = db.get_categories()
        for cat in categories:
            cat.load_data()
        categories = [c for c in categories if not c.is_total]
        # Delete categories if they don't exists and create a name:cat map
        name2cat = {}
        for cat in categories[:]:
            if cat.name not in accountnames:
                cat.delete()
                categories.remove(cat)
            else:
                name2cat[cat.name] = cat
        # Determine date ranges for which we compute amounts
        dr = MonthRange(date.today())
        dateranges = [dr]
        for _ in xrange(MONTHS_TO_FILL-1):
            dr = dr.prev()
            dateranges.append(dr)
        # Add/update categories
        self.document.oven.continue_cooking(until_date=date.today())
        currency = self.document.app.default_currency
        for account in accounts:
            if account.name not in name2cat:
                cat = db.new_category()
                cat.name = account.name
                cat.is_recurring = self.atable.is_recurring(account)
            else:
                cat = name2cat[account.name]
            cat.is_income = account.type == AccountType.Income
            cat.save_data()
            for dr in dateranges:
                cash_flow = account.entries.normal_cash_flow(dr, currency=currency)
                if not cash_flow:
                    continue
                cell = cat.get_cell(dr.start)
                cell.amount = int(cash_flow.value*100)
                cell.save_data()
        db.fix_category_order()
    
    def launch_cc(self):
        # Launch CC with moneyGuru's database as an argument
        pass
    
    