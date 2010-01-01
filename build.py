# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os
import os.path as op

import yaml

from hsdocgen import generate_help, filters

def main():
    conf = yaml.load(open('conf.yaml'))
    ui = conf['ui']
    dev = conf['dev']
    print "Building moneyGuru with UI {0}".format(ui)
    if dev:
        print "Building in Dev mode"
    print "Generating Help"
    windows = sys.platform == 'win32'
    tix = filters.tixgen("https://hardcoded.lighthouseapp.com/projects/31473-moneyguru/tickets/{0}")
    basepath = op.abspath('help')
    destpath = op.abspath(op.join('help', 'moneyguru_help'))
    generate_help.main(basepath, destpath, force_render=not dev, tix=tix, windows=windows)
    if ui == 'cocoa':
        os.chdir('cocoa')
        if dev:
            os.system('python gen.py --dev')
        else:
            os.system('python gen.py')
        os.chdir('..')
    elif ui == 'qt':
        os.chdir('qt')
        os.system('python gen.py')
        os.chdir('..')

if __name__ == '__main__':
    main()
