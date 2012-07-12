import sys
import os
import os.path as op

from setuptools import setup, Extension

sys.path.insert(1, op.abspath('src'))

from hscommon.build import move_all

exts = [
	Extension('_amount', [op.join('modules', 'amount.c')])
]
setup(
    script_args = ['build_ext', '--inplace'],
    ext_modules = exts,
)
move_all('_amount*', op.join('src', 'core', 'model'))
