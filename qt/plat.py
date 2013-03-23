# Created By: Virgil Dupras
# Created On: 2010-04-02
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op

if op.exists(__file__):
    # We want to get the absolute path or our root folder. We know that in that folder we're
    # inside qt, so we just go back a level.
    BASE_PATH = op.abspath(op.join(op.dirname(__file__), '..'))
else:
    # We're under a freezed environment. Our base path is ''.
    BASE_PATH = ''
HELP_PATH = op.join(BASE_PATH, 'help')