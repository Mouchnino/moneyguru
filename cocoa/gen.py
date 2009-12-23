#!/usr/bin/env python
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
sys.path.insert(0, 'py') # for hsutil and hsdocgen
import os

from help import gen
from moneyguru.app import Application as MoneyGuruApp

gen.generate()
os.system('/Developer/Applications/Utilities/Help\\ Indexer.app/Contents/MacOS/Help\\ Indexer help/moneyguru_help')

os.chdir('py')
os.system('python -u gen.py')
os.chdir('..')

print 'Generating Info.plist'
contents = open('InfoTemplate.plist').read()
contents = contents.replace('{version}', MoneyGuruApp.VERSION)
open('Info.plist', 'w').write(contents)