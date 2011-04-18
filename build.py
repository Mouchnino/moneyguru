# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import os
import os.path as op
import shutil
import json

from setuptools import setup, Extension

from hscommon import sphinxgen
from hscommon.build import (print_and_do, build_all_qt_ui, copy_packages, build_cocoa_localization,
    build_all_qt_locs)

def move(src, dst):
    if not op.exists(src):
        return
    if op.exists(dst):
        os.remove(dst)
    print('Moving %s --> %s' % (src, dst))
    os.rename(src, dst)

def build_all_cocoa_locs(basedir):
    locs = [name for name in os.listdir(basedir) if name.endswith('.lproj')]
    locs.remove('en.lproj')
    model_path = op.join(basedir, 'en.lproj')
    for loc in locs:
        loc_path = op.join(basedir, loc)
        print("Building {0} localizations".format(loc_path))
        build_cocoa_localization(model_path, loc_path)

def build_cocoa(dev):
    from pluginbuilder import build_plugin
    if not dev:
        print("Building help index")
        help_path = op.abspath('help/moneyguru_help')
        os.system('open -a /Developer/Applications/Utilities/Help\\ Indexer.app {0}'.format(help_path))
    
    build_all_cocoa_locs('cocoalib')
    build_all_cocoa_locs('cocoa')
        
    print("Building mg_cocoa.plugin")
    if not dev:
        copy_packages(['core', 'hscommon'], 'build')
    shutil.copy('cocoa/mg_cocoa.py', 'build')
    os.chdir('build')
    # We have to exclude PyQt4 specifically because it's conditionally imported in hscommon.trans
    build_plugin('mg_cocoa.py', excludes=['PyQt4'], alias=dev)
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
    print('Generating Info.plist')
    # We import this here because we don't want opened module to prevent us replacing .pyd files.
    from core.app import Application as MoneyGuruApp
    contents = open('InfoTemplate.plist').read()
    contents = contents.replace('{version}', MoneyGuruApp.VERSION)
    open('Info.plist', 'w').write(contents)
    print("Building the XCode project")
    args = []
    if dev:
        args.append('-configuration dev')
    else:
        args.append('-configuration release')
    args = ' '.join(args)
    os.system('xcodebuild {0}'.format(args))
    os.chdir('..')
    print("Creating the run.py file")
    subfolder = 'dev' if dev else 'release'
    app_path = 'cocoa/build/{0}/moneyGuru.app'.format(subfolder)
    tmpl = open('run_template_cocoa.py', 'rt').read()
    run_contents = tmpl.replace('{{app_path}}', app_path)
    open('run.py', 'wt').write(run_contents)

def build_qt(dev):
    print("Converting .ts to .qm")
    build_all_qt_locs(op.join('qt', 'lang'), extradirs=[op.join('qtlib', 'lang')])
    print("Building UI units")
    uipath = op.join('qt', 'ui')
    build_all_qt_ui(uipath)
    # This below is a ugly hack to work around the broken resource import system in pyuic
    for filename in os.listdir(uipath):
        if not filename.endswith('.py'):
            continue
        contents = open(op.join(uipath, filename), 'rt', encoding='utf-8').read()
        if 'import mg_rc' not in contents:
            continue
        contents = contents.replace('import mg_rc', 'from .. import mg_rc')
        open(op.join(uipath, filename), 'wt', encoding='utf-8').write(contents)
    qrc_path = op.join('qt', 'mg.qrc')
    pyrc_path = op.join('qt', 'mg_rc.py')
    print_and_do("pyrcc4 -py3 {0} > {1}".format(qrc_path, pyrc_path))
    print("Creating the run.py file")
    shutil.copy('run_template_qt.py', 'run.py')

def build_help():
    print("Generating Help")
    platform = 'osx' if sys.platform == 'darwin' else 'win'
    current_path = op.abspath('.')
    confpath = op.join(current_path, 'help', 'conf.tmpl')
    help_basepath = op.join(current_path, 'help', 'en')
    help_destpath = op.join(current_path, 'build', 'help')
    changelog_path = op.join(current_path, 'help', 'changelog')
    tixurl = "https://hardcoded.lighthouseapp.com/projects/31473-moneyguru/tickets/{0}"
    confrepl = {'platform': platform}
    sphinxgen.gen(help_basepath, help_destpath, changelog_path, tixurl, confrepl, confpath)

def main():
    conf = json.load(open('conf.json'))
    ui = conf['ui']
    dev = conf['dev']
    print("Building moneyGuru with UI {0}".format(ui))
    if dev:
        print("Building in Dev mode")
    if op.exists('build'):
        shutil.rmtree('build')
    os.mkdir('build')
    build_help()
    if dev:
        print("Generating devdocs")
        print_and_do('sphinx-build devdoc devdoc_html')
    print("Building C extensions")
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
