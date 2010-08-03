# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-08-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

import sqlite3 as sqlite
from datetime import date, timedelta

# month values in CC DB are archived NSDate which represent the number of seconds since epoch, which
# is the first moment of 2001/01/01. Dates in the DB are supposed to be the first day of the month,
# but they seem to be a little off. Therefore, if the day is the last of the month, we increase the
# month.

EPOCH = date(2001, 1, 1)

def decode_date(encoded_date):
    result = EPOCH + timedelta(seconds=encoded_date)
    if result.day >= 28:
        result = result + timedelta(days=1)
    return date(result.year, result.month, 1)

def encode_date(decoded_date):
    td = decoded_date - EPOCH
    return td.total_seconds()

class Category(object):
    def __init__(self, db, pk=None):
        # pk=None equal new record not yet in db
        self.db = db
        self.con = db.con
        self.pk = pk
        self.name = ''
        self.is_income = False
        self.is_recurring = True
        self.is_total = False
        self.month2cell = {}
    
    def _create(self):
        # We set a row index of 0 for now. Fix row indexes in batch afterwards.
        # We have to specify all values or else they get NULL instead of 0
        sql = "insert into ZCATEGORY(Z_ENT, Z_OPT, ZROWINDEX, ZSCENARIO, ZISTOTAL, ZISHIDDEN, "\
            "ZISTOTALALL) values(2, 1, 0, ?, 0, 0, 0)"
        cur = self.con.execute(sql, [self.db.main_scenario_pk])
        sql = "select Z_PK from ZCATEGORY where rowid = ?"
        [row] = self.con.execute(sql, [cur.lastrowid])
        self.pk = row[0]
    
    def _load_cells(self):
        sql = "select Z_PK from ZCELL where ZCATEGORY = ?"
        cur = self.con.execute(sql, [self.pk])
        for row in cur:
            cell = Cell(self, row[0])
            cell.load_data()
            self.month2cell[cell.date] = cell
    
    def get_cell(self, month):
        if month in self.month2cell:
            return self.month2cell[month]
        else:
            cell = Cell(self)
            cell.date = month
            self.month2cell[month] = cell
            return cell
    
    def load_data(self):
        if self.pk is None:
            return
        sql = "select ZNAME, ZISINCOME, ZISRECURRING, ZISTOTAL from ZCATEGORY where Z_PK = ?"
        [row] = self.con.execute(sql, [self.pk])
        self.name = row[0]
        self.is_income = bool(row[1])
        self.is_recurring = bool(row[2])
        self.is_total = bool(row[3])
        self._load_cells()
    
    def save_data(self):
        if self.pk is None:
            self._create()
        sql = "update ZCATEGORY set ZNAME=?, ZISINCOME=?, ZISRECURRING=? where Z_PK=?"
        isincomeval = 1 if self.is_income else 0
        isrecval = 1 if self.is_recurring else 0
        self.con.execute(sql, [self.name, isincomeval, isrecval, self.pk])
    

class Cell(object):
    def __init__(self, category, pk=None):
        self.db = category.db
        self.con = self.db.con
        self.pk = pk
        self.category = category
        self.date = None
        self.amount = 0
    
    def _create(self):
        assert self.category.pk is not None
        # We have to specify all values or else they get NULL instead of 0
        sql = "insert into ZCELL(Z_ENT, Z_OPT, ZCATEGORY, ZISAVERAGEPLAN, ZPLANAMOUNT, ZPLANSTEP, "\
            "ZISAUTO) values(3, 1, ?, 0, 0, 1, 0)"
        cur = self.con.execute(sql, [self.category.pk])
        self.pk = cur.lastrowid
    
    def load_data(self):
        if self.pk is None:
            return
        sql = "select ZMONTH, ZACTUALAMOUNT from ZCELL where Z_PK = ?"
        [row] = self.con.execute(sql, [self.pk])
        self.date = decode_date(row[0])
        self.amount = row[1]
    
    def save_data(self):
        if self.pk is None:
            self._create()
        sql = "update ZCELL set ZMONTH=?, ZPLANSTARTMONTH=?, ZACTUALAMOUNT=? where Z_PK=?"
        month = encode_date(self.date)
        self.con.execute(sql, [month, month, self.amount, self.pk])
    

class CashculatorDB(object):
    def __init__(self, dbpath):
        self.con = sqlite.connect(dbpath)
        sql = "select Z_PK from ZSCENARIO where ZNAME like 'moneyGuru'"
        cur = self.con.execute(sql)
        firstrow = cur.fetchone()
        if firstrow is None:
            sql = "select ZSETTINGS, ZVISIBLEHORIZON from ZSCENARIO"
            cur = self.con.execute(sql)
            settings_pk, visiblehor = cur.fetchone()
            sql = "insert into ZSCENARIO(Z_ENT, Z_OPT, ZROWINDEX, ZSETTINGS, ZVISIBLEHORIZON, ZNAME) "\
                "values(5, 1, 42, ?, ?, 'moneyGuru')"
            cur = self.con.execute(sql, [settings_pk, visiblehor])
            self.main_scenario_pk = cur.lastrowid
            self.con.commit()
        else:
            self.main_scenario_pk = firstrow[0]
    
    def fix_category_order(self):
        # Fix row indexes of categories depending on their recurrence status
        sql = "delete from ZCATEGORY where ZISTOTAL = 1 and ZSCENARIO = ?"
        self.con.execute(sql, [self.main_scenario_pk])
        for is_income in [0, 1]:
            basename = "income" if is_income else "expense"
            sql = "select Z_PK from ZCATEGORY where ZISINCOME = ? and ZISRECURRING = ? and ZSCENARIO = ?"
            cur = self.con.execute(sql, [is_income, 1, self.main_scenario_pk])
            recurrent_pks = [row[0] for row in cur]
            cur = self.con.execute(sql, [is_income, 0, self.main_scenario_pk])
            nonrecurrent_pks = [row[0] for row in cur]
            running_index = 0
            # First, the recurring total
            sqlfortotal = "insert into ZCATEGORY(Z_ENT, Z_OPT, ZISTOTAL, ZISHIDDEN, ZROWINDEX, "\
                "ZISTOTALALL, ZISINCOME, ZISRECURRING, ZSCENARIO, ZNAME) values(2, 1, 1, 0, ?, ?, "\
                "?, ?, ?, ?)"
            sqlforcat = "update ZCATEGORY set ZROWINDEX = ? where Z_PK = ?"
            name = "Recurring {0}".format(basename)
            self.con.execute(sqlfortotal, [running_index, 0, is_income, 1, self.main_scenario_pk, name])
            running_index += 1
            for pk in recurrent_pks:
                self.con.execute(sqlforcat, [running_index, pk])
                running_index += 1
            name = "Non-recurring {0}".format(basename)
            self.con.execute(sqlfortotal, [running_index, 0, is_income, 0, self.main_scenario_pk, name])
            running_index += 1
            for pk in nonrecurrent_pks:
                self.con.execute(sqlforcat, [running_index, pk])
                running_index += 1
            self.con.execute(sqlfortotal, [running_index, 1, is_income, 0, self.main_scenario_pk, "Total"])
        self.con.commit()
    
    def get_categories(self):
        sql = "select Z_PK from ZCATEGORY where ZSCENARIO=?"
        cur = self.con.execute(sql, [self.main_scenario_pk])
        return [Category(self, row[0]) for row in cur]
    
    def new_category(self):
        return Category(self)
    
