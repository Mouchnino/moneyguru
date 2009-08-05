# Created By: Virgil Dupras
# Created On: 2008-08-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ...gui.table import Table

def test_in():
    # When a table is in a list, doing "in list" with another instance returns false, even if
    # they're the same as lists.
    table = Table()
    some_list = [table]
    assert Table() not in some_list

