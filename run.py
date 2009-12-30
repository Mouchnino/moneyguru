# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os
import os.path as op

import yaml

import help.gen

def main():
    conf = yaml.load(open('conf.yaml'))
    ui = conf['ui']
    print "Running moneyGuru with UI {0}".format(ui)
    if ui == 'cocoa':
        os.system('open cocoa/build/Release/moneyGuru.app')
    elif ui == 'qt':
        os.environ['PYTHONPATH'] = '{0}:$PYTHONPATH'.format(op.abspath('.'))
        os.chdir('qt')
        os.system('python start.py')
        os.chdir('..')

if __name__ == '__main__':
    main()