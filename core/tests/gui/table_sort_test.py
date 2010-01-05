# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..base import TestCase

class TransactionsWithInfoFilledUp(TestCase):
    # Transactions with all kinds of info filled up (desc, payee, checkno...)
    def setUp(self):
        self.create_instances()
        self.add_txn(date='30/11/2009', description='desc', payee='payee', checkno='123',
            from_='from', to='to', amount='42')
        self.add_txn(date='01/12/2009', description='aaa', payee='zzz', checkno='321',
            from_='aaa', to='zzz', amount='41')
        self.add_txn(date='02/12/2009', description='zzz', payee='aaa', checkno='000',
            from_='zzz', to='aaa', amount='43')
    
    def test_sort_by_date(self):
        # Sorting by date use the datetime value for sorting, not the string value.
        self.ttable.sort_by('date')
        eq_(self.ttable[0].date, '30/11/2009')
        eq_(self.ttable[1].date, '01/12/2009')
        eq_(self.ttable[2].date, '02/12/2009')
    
    def test_sort_by_description(self):
        # Sorting by description works
        self.ttable.sort_by('description')
        eq_(self.ttable[0].description, 'aaa')
        eq_(self.ttable[1].description, 'desc')
        eq_(self.ttable[2].description, 'zzz')
    
    def test_sort_by_from(self):
        # we deal with the from --> from_ escaping. At the time this test was written, it didn't
        # fail because the we're just fetching '_from', but it's still a case that can very likely
        # fail in future re-factorings.
        self.ttable.sort_by('from')
        eq_(self.ttable[0].from_, 'aaa')
        eq_(self.ttable[1].from_, 'from')
        eq_(self.ttable[2].from_, 'zzz')
    
    