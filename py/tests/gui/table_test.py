# Unit Name: moneyguru.gui.table_test
# Created By: Virgil Dupras
# Created On: 2008-08-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from ...gui.table import Table

def test_in():
    # When a table is in a list, doing "in list" with another instance returns false, even if
    # they're the same as lists.
    table = Table()
    some_list = [table]
    assert Table() not in some_list

