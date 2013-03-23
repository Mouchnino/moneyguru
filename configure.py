# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from optparse import OptionParser
import json

from hscommon.plat import ISOSX

def main(ui, dev):
    if ui not in ('cocoa', 'qt'):
        ui = 'cocoa' if ISOSX else 'qt'
    build_type = 'Dev' if dev else 'Release'
    print("Configuring moneyGuru for UI {0} ({1})".format(ui, build_type))
    conf = {
        'ui': ui,
        'dev': dev,
    }
    json.dump(conf, open('conf.json', 'w'))

if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('--ui', dest='ui',
        help="Type of UI to build. 'qt' or 'cocoa'. Default is determined by your system.")
    parser.add_option('--dev', action='store_true', dest='dev', default=False,
        help="If this flag is set, will configure for dev builds.")
    (options, args) = parser.parse_args()
    main(options.ui, options.dev)
