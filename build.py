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
import shutil

from setuptools import setup, Extension
import yaml

from hsdocgen import helpgen
from hsutil.build import print_and_do, build_all_qt_ui, copy_packages, build_cocoa_localization

def move(src, dst):
    if not op.exists(src):
        return
    if op.exists(dst):
        os.remove(dst)
    print 'Moving %s --> %s' % (src, dst)
    os.rename(src, dst)

def build_all_cocoa_locs(basedir):
    locs = [name for name in os.listdir(basedir) if name.endswith('.lproj')]
    locs.remove('en.lproj')
    model_path = op.join(basedir, 'en.lproj')
    for loc in locs:
        loc_path = op.join(basedir, loc)
        print "Building {0} localizations".format(loc_path)
        build_cocoa_localization(model_path, loc_path)

def build_cocoa(dev):
    if not dev:
        print "Building help index"
        help_path = op.abspath('help/moneyguru_help')
        os.system('open -a /Developer/Applications/Utilities/Help\\ Indexer.app {0}'.format(help_path))
    
    build_all_cocoa_locs('cocoalib')
    build_all_cocoa_locs('cocoa')
        
    print "Building mg_cocoa.plugin"
    if op.exists('build'):
        shutil.rmtree('build')
    os.mkdir('build')
    if not dev:
        copy_packages(['core', 'hsutil', 'hsgui'], 'build')
    shutil.copy('cocoa/mg_cocoa.py', 'build')
    os.chdir('build')
    script_args = ['py2app', '-A'] if dev else ['py2app']
    setup(
        script_args = script_args,
        plugin = ['mg_cocoa.py'],
        setup_requires = ['py2app'],
    )
    os.chdir('..')
    pluginpath = 'cocoa/mg_cocoa.plugin'
    if op.exists(pluginpath):
        shutil.rmtree(pluginpath)
    shutil.move('build/dist/mg_cocoa.plugin', pluginpath)
    if dev:
        # In alias mode, the tweakings we do to the pythonpath aren't counted in. We have to
        # manually put a .pth in the plugin
        pthpath = op.join(pluginpath, 'Contents/Resources/dev.pth')
        open(pthpath, 'w').write(op.abspath('.'))
    os.chdir('cocoa')
    print 'Generating Info.plist'
    # We import this here because we don't want opened module to prevent us replacing .pyd files.
    from core.app import Application as MoneyGuruApp
    contents = open('InfoTemplate.plist').read()
    contents = contents.replace('{version}', MoneyGuruApp.VERSION)
    open('Info.plist', 'w').write(contents)
    print "Building the XCode project"
    args = []
    if dev:
        args.append('-configuration dev')
    else:
        args.append('-configuration release')
    args = ' '.join(args)
    os.system('xcodebuild {0}'.format(args))
    os.chdir('..')

def build_qt(dev):
    print "Converting .ts to .qm"
    langdir = op.join('qt', 'lang')
    tsfiles = [fn for fn in os.listdir(langdir) if fn.endswith('.ts')]
    for ts in tsfiles:
        print "Converting {0}".format(ts)
        os.system('lrelease {0}'.format(op.join(langdir, ts)))
    print "Building UI units"
    build_all_qt_ui(op.join('qtlib', 'ui'))
    build_all_qt_ui(op.join('qt', 'ui'))
    qrc_path = op.join('qt', 'mg.qrc')
    pyrc_path = op.join('qt', 'mg_rc.py')
    print_and_do("pyrcc4 {0} > {1}".format(qrc_path, pyrc_path))

def main():
    conf = yaml.load(open('conf.yaml'))
    ui = conf['ui']
    dev = conf['dev']
    print "Building moneyGuru with UI {0}".format(ui)
    if dev:
        print "Building in Dev mode"
    print "Generating Help"
    windows = sys.platform == 'win32'
    profile = 'win_en' if windows else 'osx_en'
    basepath = op.abspath('help')
    destpath = op.abspath(op.join('help', 'moneyguru_help'))
    helpgen.gen(basepath, destpath, profile=profile)
    print "Building C extensions"
    exts = []
    exts.append(Extension('_amount', [op.join('core', 'modules', 'amount.c')]))
    setup(
        script_args = ['build_ext', '--inplace'],
        ext_modules = exts,
    )
    move('_amount.so', op.join('core', 'model', '_amount.so'))
    move('_amount.pyd', op.join('core', 'model', '_amount.pyd'))
    if ui == 'cocoa':
        build_cocoa(dev)
    elif ui == 'qt':
        build_qt(dev)

if __name__ == '__main__':
    main()
