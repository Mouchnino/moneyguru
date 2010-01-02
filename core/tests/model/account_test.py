# coding: utf-8 
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import xmlrpclib
from datetime import date

from hsutil.currency import USD, CAD

from ..base import TestCase
from ...model import currency
from ...model.account import Account, Group, AccountList, ASSET
from ...model.amount import Amount
from ...model.date import MonthRange
from ...model.oven import Oven
from ...model.transaction import Transaction, Entry
from ...model.transaction_list import TransactionList

class AccountComparison(TestCase):
    def test_comparison(self):
        """Accounts are sorted by name. The sort is insensitive to case and accents."""
        bell = Account(u'Bell', USD, ASSET)
        belarus = Account(u'Bélarus', USD, ASSET)
        achigan = Account(u'achigan', USD, ASSET)
        accounts = [bell, belarus, achigan]
        self.assertEqual(sorted(accounts), [achigan, belarus, bell])

    def test_equality(self):
        """Two different account objects are never equal."""
        zoo1 = Account(u'Zoo', USD, ASSET)
        zoo2 = Account(u'Zoo', USD, ASSET)
        zoo3 = Account(u'Zoö', USD, ASSET)
        self.assertEqual(zoo1, zoo1)
        self.assertNotEqual(zoo1, zoo2)
        self.assertNotEqual(zoo1, zoo3)

class GroupComparison(TestCase):
    def test_comparison(self):
        """Groups are sorted by name. The sort is insensitive to case and accents."""
        bell = Group(u'Bell', ASSET)
        belarus = Group(u'Bélarus', ASSET)
        achigan = Group(u'achigan', ASSET)
        groups = [bell, belarus, achigan]
        self.assertEqual(sorted(groups), [achigan, belarus, bell])

    def test_equality(self):
        """Two different group objects are never equal."""
        zoo1 = Group(u'Zoo', ASSET)
        zoo2 = Group(u'Zoo', ASSET)
        zoo3 = Group(u'Zoö', ASSET)
        self.assertEqual(zoo1, zoo1)
        self.assertNotEqual(zoo1, zoo2)
        self.assertNotEqual(zoo1, zoo3)


class OneAccount(TestCase):
    def setUp(self):
        USD.set_CAD_value(1.1, date(2007, 12, 31))
        USD.set_CAD_value(0.9, date(2008, 1, 1))
        USD.set_CAD_value(0.8, date(2008, 1, 2))
        USD.set_CAD_value(0.7, date(2008, 1, 3))
        self.account = Account('Checking', USD, ASSET)
        accounts = AccountList(CAD)
        accounts.add(self.account)
        transactions = TransactionList([
            Transaction(date(2007, 12, 31), account=self.account, amount=Amount(20, USD)),
            Transaction(date(2008, 1, 1), account=self.account, amount=Amount(100, USD)),
            Transaction(date(2008, 1, 2), account=self.account, amount=Amount(50, USD)),
            Transaction(date(2008, 1, 3), account=self.account, amount=Amount(70, CAD)),
            Transaction(date(2008, 1, 31), account=self.account, amount=Amount(2, USD)),
        ])
        oven = Oven(accounts, transactions, [], [])
        oven.cook(date.min, date.max)
    
    def test_balance(self):
        self.assertEqual(self.account.balance(date(2007, 12, 31)), Amount(20, USD))
        
        # The balance is converted using the rate on the day the balance is
        # requested.
        self.assertEqual(self.account.balance(date(2007, 12, 31), currency=CAD), Amount(20 * 1.1, CAD))

    def test_cash_flow(self):
        range = MonthRange(date(2008, 1, 1))
        self.assertEqual(self.account.cash_flow(range), Amount(252, USD))

        # Each entry is converted using the entry's day rate.
        self.assertEqual(self.account.cash_flow(range, CAD), Amount(201.40, CAD))

