# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-04-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys

if sys.platform == 'win32':
    from plat_win import *
elif sys.platform == 'linux2':
    from plat_lnx import *
elif sys.platform == 'darwin':
    from plat_osx import *
else:
    print "Unsupported platform"
