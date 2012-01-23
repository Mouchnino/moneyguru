# Created By: Virgil Dupras
# Created On: 2010-08-02
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# NOTE: The cashculator integration code has no automated tests. Developing it is so much try/error
# and the wanted database values are so much subject to change that I found maintaining tests
# beside it counter-productive. Therefore, be careful when modifying this code, there's no safety net.

import subprocess
from datetime import date
import os.path as op

from cocoa import proxy
from hscommon import io
from hscommon.path import Path
from hscommon.trans import tr

from ..const import PaneType
from ..model.account import AccountType
from ..model.cashculator import CashculatorDB
from ..model.date import MonthRange, ONE_DAY
from .base import BaseView
from .cashculator_account_table import CashculatorAccountTable

MONTHS_TO_FILL = 4
MSG_NO_DB = tr("Exported database not present. Click on Export Accounts first.")
MSG_NO_BASE_DB = tr("Base Cashculator database not present. You must run and quit Cashculator at least "\
    "once before using the export feature.")


class CashculatorView(BaseView):
    VIEW_TYPE = PaneType.Cashculator
    
    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        self._mgccdbpath = None
        self._ccdbpath = None
        self._db = None
        self._categories = None # name: cat
        self._needs_reset = False
        self.atable = CashculatorAccountTable(self)
        self.set_children([self.atable])
    
    #--- Private
    def _ensure_paths(self):
        if self._ccdbpath is not None:
            return
        ccdb_folder = op.expanduser(proxy.prefValue_inDomain_('CCDB_Folder', 'com.apparentsoft.cashculator'))
        self._ccdbpath = Path(ccdb_folder) + 'CCDB'
        appsupport = Path(proxy.getAppdataPath())
        self._mgccdbpath = appsupport + 'moneyGuru/cc/CCDB'
    
    def _open_db(self):
        # If there's no CC db in moneyGuru's appdata folder, copy a model from CC's appdata.
        if not self.has_db():
            if not io.exists(self._mgccdbpath[:-1]):
                io.makedirs(self._mgccdbpath[:-1])
            io.copy(self._ccdbpath, self._mgccdbpath)
        self._db = CashculatorDB(str(self._mgccdbpath))
    
    #--- Public
    def export_db(self):
        self._ensure_paths()
        if self._ccdbpath is None or not io.exists(self._ccdbpath):
            self.mainwindow.show_message(MSG_NO_BASE_DB)
            return
        # Determine date ranges for which we compute amounts
        dr = MonthRange(date.today())
        dateranges = [dr]
        for _ in range(MONTHS_TO_FILL-1):
            dr = dr.prev()
            dateranges.append(dr)
        # Update CC db with actual data from moneyGuru.
        self.document.oven.continue_cooking(until_date=date.today())
        currency = self.document.default_currency
        db = self.get_db()
        accounts = [row.account for row in self.atable]
        categories = self.get_categories()
        for account in accounts:
            if account.name not in categories:
                cat = db.new_category()
                cat.name = account.name
            else:
                cat = categories[account.name]
            cat.is_recurring = self.atable.is_recurring(account.name)
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
        # Now set starting balances
        accounts = {a for a in self.document.accounts if a.is_balance_sheet_account()}
        accounts -= self.document.excluded_accounts
        for dr in dateranges:
            baldate = dr.start - ONE_DAY
            nw =  sum(a.entries.balance(date=baldate, currency=currency) for a in accounts)
            if nw:
                nw = int(nw.value*100)
            db.set_balance(dr.start, nw)
        self._categories = None
    
    def launch_cc(self):
        # Launch CC with moneyGuru's database as an argument. Don't forget to call reset_ccdb a
        # little while afterwards.
        if not self.has_db():
            self.mainwindow.show_message(MSG_NO_DB)
            return
        # XXX Add CocoaProxy.setPrefValue_value_inDomain_
        cmd = "defaults write com.apparentsoft.cashculator CCDB_Folder \"{0}\""
        cmd = cmd.format(str(self._mgccdbpath[:-1]))
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        self._needs_reset = True
        cmd = "open -a Cashculator"
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
    
    def get_db(self):
        if self._db is None:
            self._open_db()
        return self._db
    
    def get_categories(self): # name: cat
        if self._categories is None:
            db = self.get_db()
            categories = db.get_categories()
            for cat in categories:
                cat.load_data()
            categories = [c for c in categories if not c.is_total]
            self._categories = {}
            for cat in categories:
                self._categories[cat.name] = cat
        return self._categories
    
    def has_db(self):
        self._ensure_paths()
        return (self._mgccdbpath is not None) and io.exists(self._mgccdbpath)
    
    def reset_ccdb(self):
        # Sets CC's db back to its old value
        cmd = "defaults write com.apparentsoft.cashculator CCDB_Folder \"{0}\""
        cmd = cmd.format(str(self._ccdbpath[:-1]))
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        self._needs_reset = False
    
    #--- Events
    def document_will_close(self):
        if self._needs_reset:
            self.reset_ccdb()
    
