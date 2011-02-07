# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import os
import os.path as op
import compileall
import shutil
import json

from core.app import Application as MoneyGuru
from hscommon.build import (build_dmg, copy_packages, build_debian_changelog, copy_qt_plugins,
    print_and_do)

def package_windows(dev):
    if sys.platform != "win32":
        print("Qt packaging only works under Windows.")
        return
    
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
    
    help_path = 'build\\help'
    print("Copying {0} to dist\\help".format(help_path))
    shutil.copytree(help_path, 'dist\\help')
    
    if not dev:
        # AdvancedInstaller.com has to be in your PATH
        # this is so we don'a have to re-commit installer.aip at every version change
        shutil.copy('qt\\installer.aip', 'installer_tmp.aip')
        print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % MoneyGuru.VERSION)
        print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
        os.remove('installer_tmp.aip')
    

def package_debian():
    destpath = op.join('build', 'moneyguru-{0}'.format(MoneyGuru.VERSION))
    if op.exists(destpath):
        shutil.rmtree(destpath)
    srcpath = op.join(destpath, 'src')
    os.makedirs(srcpath)
    shutil.copy('run.py', op.join(srcpath, 'run.py'))
    copy_packages(['qt', 'hscommon', 'core', 'qtlib'], srcpath)
    import sip, PyQt4, sgmllib
    shutil.copy(sip.__file__, srcpath)
    qtsrcpath = op.dirname(PyQt4.__file__)
    qtdestpath = op.join(srcpath, 'PyQt4')
    os.makedirs(qtdestpath)
    shutil.copy(op.join(qtsrcpath, '__init__.py'), qtdestpath)
    shutil.copy(op.join(qtsrcpath, 'Qt.so'), qtdestpath)
    shutil.copy(op.join(qtsrcpath, 'QtCore.so'), qtdestpath)
    shutil.copy(op.join(qtsrcpath, 'QtGui.so'), qtdestpath)
    shutil.copy(sgmllib.__file__, srcpath)
    shutil.copytree('debian', op.join(destpath, 'debian'))
    build_debian_changelog(op.join('help', 'changelog'), op.join(destpath, 'debian', 'changelog'),
        'moneyguru', from_version='1.8.0')
    shutil.copytree(op.join('build', 'help'), op.join(srcpath, 'help'))
    shutil.copy(op.join('images', 'logo_small.png'), srcpath)
    compileall.compile_dir(srcpath)
    os.chdir(destpath)
    os.system("dpkg-buildpackage")

def main():
    conf = json.load(open('conf.json'))
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
