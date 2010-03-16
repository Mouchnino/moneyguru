# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..base import TestApp

def test_can_navigate():
    # The `can_navigate` property mirrors the date range's `can_navigate`.
    app = TestApp() # year range
    assert app.drsel.can_navigate
    app.drsel.select_year_to_date_range()
    assert not app.drsel.can_navigate
