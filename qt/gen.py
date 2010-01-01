#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import sys
sys.path.insert(0, op.abspath('..')) # for all cross-toolkit modules
from optparse import OptionParser

from hsutil.build import print_and_do, build_all_qt_ui

def main(dev):
    print "Building UI units"
    build_all_qt_ui(op.join('..', 'qtlib', 'ui'))
    build_all_qt_ui('ui')
    print_and_do("pyrcc4 mg.qrc > mg_rc.py")

if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('--dev', action='store_true', dest='dev', default=False,
        help="If this flag is set, will configure for dev builds.")
    (options, args) = parser.parse_args()
    main(options.dev)
