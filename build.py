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

from setuptools import setup
import yaml

from hsdocgen import generate_help, filters
from hsutil.build import add_to_pythonpath, print_and_do, build_all_qt_ui, copy_packages
from core.app import Application as MoneyGuruApp

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
        if not dev:
            print "Building help index"
            help_path = op.abspath('help/moneyguru_help')
            os.system('open /Developer/Applications/Utilities/Help\\ Indexer.app --args {0}'.format(help_path))
        
        print "Building mg_cocoa.plugin"
        if op.exists('build'):
            shutil.rmtree('build')
        os.mkdir('build')
        if not dev:
            copy_packages(['core', 'hsutil'], 'build')
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
        contents = open('InfoTemplate.plist').read()
        contents = contents.replace('{version}', MoneyGuruApp.VERSION)
        open('Info.plist', 'w').write(contents)
        print "Building the XCode project"
        os.system('xcodebuild')
        os.chdir('..')
    elif ui == 'qt':
        os.chdir('qt')
        os.system('python gen.py')
        os.chdir('..')

if __name__ == '__main__':
    main()
