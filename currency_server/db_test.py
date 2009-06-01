#!/usr/bin/env python
# Unit Name: currency_server.db_test
# Created By: Virgil Dupras
# Created On: 2008-04-20
# $Id$
# Copyright 2008 Hardcoded Software (http://www.hardcoded.net)

import unittest
from datetime import date
import threading

from hs.const import TESTDIR
from hs.path import Path
from hs.testcase import TestCase

from db import RatesDB


class BOCDailyImport(TestCase):
    """testdata/xml/bankofcanada_daily_rates_1_week.xml contains daily rates for a USD, EUR and PLN
    for 1 week. To be successfully imported, the currency names have to be translated to code,
    and stuff in parenthesis have to be ignored for the translation. The xml also contain some n/a
    values that have to be handled.
    """
    def setUp(self):
        self.db = RatesDB(':memory:')
        xmlpath = Path(TESTDIR) + ('xml', 'bankofcanada_daily_rates_1_week.xml')
        self.db.import_bank_of_canada_rates(unicode(xmlpath))
    
    def test_get_rates(self):
        """Try a couple of rates and make sure they're correct"""
        self.assertAlmostEqual(self.db.get_rate(date(2008, 4, 17), 'USD', 'CAD'), 1.0122)
        self.assertAlmostEqual(self.db.get_rate(date(2008, 4, 21), 'USD', 'CAD'), 1.0060)
        self.assertAlmostEqual(self.db.get_rate(date(2008, 4, 17), 'EUR', 'CAD'), 1.6103)
        self.assertAlmostEqual(self.db.get_rate(date(2008, 4, 16), 'PLN', 'CAD'), 0.4675)
    

class DBWithDailyAndMeanRate(TestCase):
    def setUp(self):
        self.db = RatesDB(':memory:')
        self.db.set_CAD_value(date(2008, 3, 25), 'USD', 1.0203)
        self.db.set_CAD_value(date(2008, 3, 24), 'USD', 1.0123)
    
    def test_get_CAD_values(self):
        """Returns the correct values, in the correct order"""
        start = date(2008, 3, 20)
        end = date(2008, 3, 25)
        result = self.db.get_CAD_values(start, end, 'USD')
        expected = [
            (date(2008, 3, 24), 1.0123),
            (date(2008, 3, 25), 1.0203),
        ]
        self.assertEqual(len(result), len(expected))
        for pair1, pair2 in zip(result, expected):
            self.assertEqual(pair1[0], pair2[0])
            if pair1[1] is None:
                self.assertTrue(pair2[1] is None)
            else:
                self.assertAlmostEqual(pair1[1], pair2[1])
    
    def test_get_CAD_values_threaded(self):
        """get_CAD_values() can be called by different threads"""
        def do():
            mydate = date(2008, 3, 24)
            result = self.db.get_CAD_values(mydate, mydate, 'USD')
            self.assertEqual(result, [(mydate, 1.0123)])
        threading.Thread(target=do).start()
        threading.Thread(target=do).start()
        self.jointhreads()
    

if __name__ == '__main__':
    unittest.main()
