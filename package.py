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
import compileall
import shutil

import yaml

from core.app import Application as MoneyGuru
from hscommon.build import (build_dmg, copy_packages, build_debian_changelog, add_to_pythonpath,
    copy_qt_plugins, print_and_do)

def package_windows(dev):
    if sys.platform != "win32":
        print("Qt packaging only works under Windows.")
        return
    add_to_pythonpath('.')
    add_to_pythonpath('qt')
    os.chdir('qt')
    
    if op.exists('dist'):
        shutil.rmtree('dist')
    
    cmd = 'cxfreeze --base-name Win32GUI --target-name "moneyGuru.exe" --icon ..\\images\\main_icon.ico start.py'
    print_and_do(cmd)
    
    if not dev:
        # Copy qt plugins
        plugin_dest = op.join('dist', 'qt4_plugins')
        plugin_names = ['accessible', 'codecs', 'iconengines', 'imageformats']
        copy_qt_plugins(plugin_names, plugin_dest)
        
        # Compress with UPX 
        libs = [name for name in os.listdir('dist') if op.splitext(name)[1] in ('.pyd', '.dll', '.exe')]
        for lib in libs:
            print_and_do("upx --best \"dist\\{0}\"".format(lib))
    
    help_path = '..\\help\\moneyguru_help'
    print("Copying {0} to dist\\help".format(help_path))
    shutil.copytree(help_path, 'dist\\help')
    
    if not dev:
        # AdvancedInstaller.com has to be in your PATH
        # this is so we don'a have to re-commit installer.aip at every version change
        shutil.copy('installer.aip', 'installer_tmp.aip')
        print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % MoneyGuru.VERSION)
        print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
        os.remove('installer_tmp.aip')
    
    os.chdir('..')

def package_debian():
    if op.exists('build'):
        shutil.rmtree('build')
    destpath = op.join('build', 'moneyguru-{0}'.format(MoneyGuru.VERSION))
    srcpath = op.join(destpath, 'src')
    os.makedirs(destpath)
    shutil.copytree('qt', srcpath)
    copy_packages(['hscommon', 'hsgui', 'core', 'qtlib', 'hsutil'], srcpath)
    shutil.copytree('debian', op.join(destpath, 'debian'))
    build_debian_changelog(op.join('help', 'changelog.yaml'), op.join(destpath, 'debian', 'changelog'), 'moneyguru', from_version='1.8.0')
    shutil.copytree(op.join('help', 'moneyguru_help'), op.join(srcpath, 'help'))
    shutil.copy(op.join('images', 'logo_small.png'), srcpath)
    compileall.compile_dir(srcpath)
    os.chdir(destpath)
    os.system("dpkg-buildpackage")

def main():
    conf = yaml.load(open('conf.yaml'))
    ui = conf['ui']
    dev = conf['dev']
    print("Packaging moneyGuru with UI {0}".format(ui))
    if ui == 'cocoa':
        build_dmg('cocoa/build/release/moneyGuru.app', '.')
    elif ui == 'qt':
        if sys.platform == "win32":
            package_windows(dev)
        elif sys.platform == "linux2":
            package_debian()
        else:
            print("Qt packaging only works under Windows or Linux.")

if __name__ == '__main__':
    main()
