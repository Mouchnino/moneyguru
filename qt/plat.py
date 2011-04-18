# Created By: Virgil Dupras
# Created On: 2010-04-02
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys

def isWindows():
    return sys.platform == 'win32'

def isLinux():
    return sys.platform == 'linux2'

def isMac():
    return sys.platform == 'darwin'

if isWindows():
    from .plat_win import *
elif isLinux():
    from .plat_lnx import *
elif isMac():
    from .plat_osx import *
else:
    print("Unsupported platform")
