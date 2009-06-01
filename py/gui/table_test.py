# Unit Name: moneyguru.gui.table_test
# Created By: Virgil Dupras
# Created On: 2008-08-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from hsutil.testcase import TestCase

from .table import Table

class NoSetup(TestCase):
    def test_in(self):
        """When a table is in a list, doing "in list" with another instance returns false, even if
        they're the same as lists.
        """
        table = Table()
        some_list = [table]
        self.assertFalse(Table() in some_list)
    
