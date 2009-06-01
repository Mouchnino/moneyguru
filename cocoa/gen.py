#!/usr/bin/env python

import os

os.chdir('help')
os.system('python -u gen.py')
os.system('/Developer/Applications/Utilities/Help\\ Indexer.app/Contents/MacOS/Help\\ Indexer moneyguru_help')
os.chdir('..')

os.chdir('py')
os.system('python -u gen.py')
os.chdir('..')