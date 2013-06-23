#!/usr/bin/env python

import sys
import os
import os.path as op
import glob
import sysconfig
from waflib import TaskGen
try:
    import hscommon
except ImportError:
    # Probably in the parent folder
    sys.path.insert(0, '..')
from hscommon.build import OSXFrameworkStructure
from hscommon.util import modified_after

# Make sure to set CFLAGS and LDFLAGS (to have correct archs and isysroot) first.

top = '.'
out = 'build'

def options(opt):
    opt.load('compiler_c')

def configure(conf):
    conf.env.CC = 'clang'
    conf.load('compiler_c')
    conf.env.FRAMEWORK_COCOA = 'Cocoa'
    conf.env.MACOSX_DEPLOYMENT_TARGET = '10.6'
    # Have the save compile/link flags as our python installation.
    conf.env.append_value('CFLAGS', sysconfig.get_config_var('CFLAGS').split(' '))
    conf.env.append_value('LINKFLAGS', sysconfig.get_config_var('LDFLAGS').split(' '))
    conf.env.append_value('LINKFLAGS', ['-install_name', '@rpath/PSMTabBarControl.framework/PSMTabBarControl'])

def build(ctx):
    ctx.shlib(
        features      = 'c cshlib',
        target        = ctx.bldnode.make_node('PSMTabBarControl'),
        source        = ctx.srcnode.ant_glob('*.m'),
        includes      = [ctx.srcnode],
        use           = 'COCOA',
    )

def build_framework(ctx):
    fmk = OSXFrameworkStructure('PSMTabBarControl.framework')
    if not modified_after('build/PSMTabBarControl', fmk.executablepath):
        print("No need to build the PSMTabBarControl framework, it's up-to-date.")
        return
    fmk.create('Info.plist')
    fmk.copy_executable('build/PSMTabBarControl')
    fmk.copy_headers(*glob.glob('*.h'))
    fmk.copy_resources(*glob.glob('images/*.*'))
    fmk.create_symlinks()

@TaskGen.extension('.m')
def m_hook(self, node):
    return self.create_compiled_task('c', node)

