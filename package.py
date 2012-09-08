# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op
import compileall
import shutil
import json
from argparse import ArgumentParser

from core.app import Application as MoneyGuru
from hscommon.plat import ISWINDOWS, ISLINUX
from hscommon.build import (copy_packages, build_debian_changelog, copy_qt_plugins, print_and_do,
    move, copy_all, setup_package_argparser, package_cocoa_app_in_dmg)

def parse_args():
    parser = ArgumentParser()
    setup_package_argparser(parser)
    parser.add_argument('--source', action='store_true', dest='source_pkg',
        help="Build only a source debian package (Linux only).")
    return parser.parse_args()

def package_windows(dev):
    if op.exists('dist'):
        shutil.rmtree('dist')
    
    cmd = 'cxfreeze --base-name Win32GUI --target-name "moneyGuru.exe" --icon images\\main_icon.ico run.py'
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
    
    shutil.copytree('build\\help', 'dist\\help')
    shutil.copytree('build\\locale', 'dist\\locale')
    shutil.copytree('plugin_examples', 'dist\\plugin_examples')
    
    if not dev:
        # AdvancedInstaller.com has to be in your PATH
        # this is so we don'a have to re-commit installer.aip at every version change
        shutil.copy('qt\\installer.aip', 'installer_tmp.aip')
        print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % MoneyGuru.VERSION)
        print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
        os.remove('installer_tmp.aip')
    

def package_debian(source_pkg):
    destpath = op.join('build', 'moneyguru-{0}'.format(MoneyGuru.VERSION))
    if op.exists(destpath):
        shutil.rmtree(destpath)
    srcpath = op.join(destpath, 'src')
    os.makedirs(srcpath)
    shutil.copy('run.py', op.join(srcpath, 'run.py'))
    copy_packages(['qt', 'hscommon', 'core', 'qtlib', 'plugin_examples'], srcpath)
    import sgmllib
    shutil.copy(sgmllib.__file__, srcpath)
    shutil.copytree('debian', op.join(destpath, 'debian'))
    move(op.join(destpath, 'debian', 'Makefile'), op.join(destpath, 'Makefile'))
    move(op.join(destpath, 'debian', 'build_modules.py'), op.join(destpath, 'build_modules.py'))
    os.mkdir(op.join(destpath, 'modules'))
    copy_all(op.join('core', 'modules', '*.*'), op.join(destpath, 'modules'))
    build_debian_changelog(op.join('help', 'changelog'), op.join(destpath, 'debian', 'changelog'),
        'moneyguru', from_version='1.8.0')
    shutil.copytree(op.join('build', 'help'), op.join(srcpath, 'help'))
    shutil.copytree(op.join('build', 'locale'), op.join(srcpath, 'locale'))
    shutil.copy(op.join('images', 'logo_small.png'), srcpath)
    compileall.compile_dir(srcpath)
    os.chdir(destpath)
    cmd = "dpkg-buildpackage"
    if source_pkg:
        cmd += " -S"
    os.system(cmd)

def main():
    args = parse_args()
    conf = json.load(open('conf.json'))
    ui = conf['ui']
    dev = conf['dev']
    print("Packaging moneyGuru with UI {0}".format(ui))
    if ui == 'cocoa':
        package_cocoa_app_in_dmg('build/moneyGuru.app', '.', args)
    elif ui == 'qt':
        if ISWINDOWS:
            package_windows(dev)
        elif ISLINUX:
            package_debian(args.source_pkg)
        else:
            print("Qt packaging only works under Windows or Linux.")

if __name__ == '__main__':
    main()
