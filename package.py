# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
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
import platform

from core.app import Application as MoneyGuru
from hscommon.plat import ISWINDOWS, ISLINUX
from hscommon.build import (copy_packages, build_debian_changelog, copy_qt_plugins, print_and_do,
    move, copy_all, setup_package_argparser, package_cocoa_app_in_dmg)
from hscommon.util import find_in_path

def parse_args():
    parser = ArgumentParser()
    setup_package_argparser(parser)
    return parser.parse_args()

def package_windows(dev):
    if op.exists('dist'):
        shutil.rmtree('dist')
    
    is64bit = platform.architecture()[0] == '64bit'
    cmd = 'cxfreeze --base-name Win32GUI --target-name "moneyGuru.exe" --icon images\\main_icon.ico run.py'
    print_and_do(cmd)
    
    if not dev:
        # Copy qt plugins
        plugin_dest = op.join('dist', 'qt4_plugins')
        plugin_names = ['accessible', 'codecs', 'iconengines', 'imageformats']
        copy_qt_plugins(plugin_names, plugin_dest)
        
        # Compress with UPX
        if not is64bit: # UPX doesn't work on 64 bit
            libs = [name for name in os.listdir('dist') if op.splitext(name)[1] in ('.pyd', '.dll', '.exe')]
            for lib in libs:
                print_and_do("upx --best \"dist\\{0}\"".format(lib))
    
    shutil.copytree('build\\help', 'dist\\help')
    shutil.copytree('build\\locale', 'dist\\locale')
    shutil.copytree('plugin_examples', 'dist\\plugin_examples')
    if is64bit:
        # In 64bit mode, we don't install the VC redist as a prerequisite. We just bundle the
        # appropriate dlls.
        shutil.copy(find_in_path('msvcr100.dll'), 'dist')
        shutil.copy(find_in_path('msvcp100.dll'), 'dist')
    
    if not dev:
        # AdvancedInstaller.com has to be in your PATH
        # this is so we don'a have to re-commit installer.aip at every version change
        installer_file = 'qt\\installer64.aip' if is64bit else 'qt\\installer.aip'
        shutil.copy(installer_file, 'installer_tmp.aip')
        print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % MoneyGuru.VERSION)
        print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
        os.remove('installer_tmp.aip')
    
def copy_source_files(destpath, packages):
    if op.exists(destpath):
        shutil.rmtree(destpath)
    os.makedirs(destpath)
    shutil.copy('run.py', op.join(destpath, 'run.py'))
    copy_packages(packages, destpath)
    shutil.copytree(op.join('build', 'help'), op.join(destpath, 'help'))
    shutil.copytree(op.join('build', 'locale'), op.join(destpath, 'locale'))
    shutil.copy(op.join('images', 'logo_small.png'), destpath)
    shutil.copy(op.join('images', 'logo_big.png'), destpath)
    compileall.compile_dir(destpath)

def package_debian(distribution):
    version = '{}~{}'.format(MoneyGuru.VERSION, distribution)
    destpath = op.join('build', 'moneyguru-{}'.format(version))
    srcpath = op.join(destpath, 'src')
    copy_source_files(srcpath, ['qt', 'hscommon', 'core', 'qtlib', 'plugin_examples', 'sgmllib'])
    shutil.copytree('debian', op.join(destpath, 'debian'))
    move(op.join(destpath, 'debian', 'Makefile'), op.join(destpath, 'Makefile'))
    move(op.join(destpath, 'debian', 'build_modules.py'), op.join(destpath, 'build_modules.py'))
    os.mkdir(op.join(destpath, 'modules'))
    copy_all(op.join('core', 'modules', '*.*'), op.join(destpath, 'modules'))
    build_debian_changelog(op.join('help', 'changelog'), op.join(destpath, 'debian', 'changelog'),
        'moneyguru', from_version='1.8.0', distribution=distribution)
    os.chdir(destpath)
    cmd = "dpkg-buildpackage -S"
    os.system(cmd)
    os.chdir('../..')

def package_arch():
    # For now, package_arch() will only copy the source files into build/. It copies less packages
    # than package_debian because there are more python packages available in Arch (so we don't
    # need to include them).
    print("Packaging for Arch")
    srcpath = op.join('build', 'moneyguru-arch')
    copy_source_files(srcpath, ['qt', 'hscommon', 'core', 'qtlib', 'plugin_examples', 'sgmllib'])

def package_source_tgz():
    app_version = MoneyGuru.VERSION
    name = 'moneyguru-src-{}.tar.gz'.format(app_version)
    dest = op.join('build', name)
    print_and_do('hg archive -t tgz -S {}'.format(dest))

def main():
    args = parse_args()
    conf = json.load(open('conf.json'))
    ui = conf['ui']
    dev = conf['dev']
    if args.src_pkg:
        print("Creating source package for moneyGuru")
        package_source_tgz()
        return
    print("Packaging moneyGuru with UI {0}".format(ui))
    if ui == 'cocoa':
        package_cocoa_app_in_dmg('build/moneyGuru.app', '.', args)
    elif ui == 'qt':
        if ISWINDOWS:
            package_windows(dev)
        elif ISLINUX:
            distname, _, _ = platform.dist()
            if distname == 'arch':
                package_arch()
            else:
                print("Packaging for Ubuntu")
                for distribution in ['precise', 'quantal', 'raring']:
                    package_debian(distribution)
        else:
            print("Qt packaging only works under Windows or Linux.")

if __name__ == '__main__':
    main()
