# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-07
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt

MIME_NODEPATH = 'application/moneyguru.nodepath'

INDENTATION_OFFSET_ROLE = Qt.UserRole # Returns an offset for the item's indentation

EXTRA_ROLE = Qt.UserRole + 1 # Returns bitwise extra flags defined below
EXTRA_UNDERLINED = 1<<0
EXTRA_UNDERLINED_DOUBLE = 1<<1
EXTRA_SPAN_ALL_COLUMNS = 1<<2
