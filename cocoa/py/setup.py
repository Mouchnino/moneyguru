#!/usr/bin/env python
from setuptools import setup

from hsutil.build import move_testdata_out, put_testdata_back

move_log = move_testdata_out()
try:
    setup(
        plugin = ['mg_cocoa.py'],
        setup_requires = ['py2app'],
    )
finally:
    put_testdata_back(move_log)
