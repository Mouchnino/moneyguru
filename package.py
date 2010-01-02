# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os
import os.path as op

import yaml

from hsutil.build import build_dmg

def main():
    conf = yaml.load(open('conf.yaml'))
    ui = conf['ui']
    dev = conf['dev']
    if dev:
        print "You can't package in dev mode"
        return
    print "Packaging moneyGuru with UI {0}".format(ui)
    if ui == 'cocoa':
        build_dmg('cocoa/build/Release/moneyGuru.app', '.')
    elif ui == 'qt':
        if sys.platform != "win32":
            print "Qt packaging only works under Windows."
            return
        pythonpath = os.environ.get('PYTHONPATH', '')
        pythonpath = ';'.join([op.abspath('.'), pythonpath]) if pythonpath else op.abspath('.')
        os.environ['PYTHONPATH'] = pythonpath
        os.chdir('qt')
        os.system('python build.py')
        os.chdir('..')

if __name__ == '__main__':
    main()