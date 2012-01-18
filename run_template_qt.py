#!/usr/bin/env python3
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import gc
import logging
import os
import os.path as op
import sip
sip.setapi('QVariant', 1)

from PyQt4.QtCore import QFile, QTextStream, QSettings
from PyQt4.QtGui import QApplication, QIcon, QPixmap, QDesktopServices

import hscommon.trans
from hscommon.plat import ISLINUX
from qtlib.error_report_dialog import install_excepthook
import qt.mg_rc
from qt.plat import BASE_PATH

def main(argv):
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(":/logo_small")))
    app.setOrganizationName('Hardcoded Software')
    app.setApplicationName('moneyGuru')
    appdata = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
    if not op.exists(appdata):
        os.makedirs(appdata)
    logging.basicConfig(filename=op.join(appdata, 'debug.log'), level=logging.WARNING)
    if ISLINUX:
        stylesheetFile = QFile(':/stylesheet_lnx')
    else:
        stylesheetFile = QFile(':/stylesheet_win')
    stylesheetFile.open(QFile.ReadOnly)
    textStream = QTextStream(stylesheetFile)
    style = textStream.readAll()
    stylesheetFile.close()
    app.setStyleSheet(style)
    settings = QSettings()
    lang = settings.value('Language').toString()
    locale_folder = op.join(BASE_PATH, 'locale')
    hscommon.trans.install_gettext_trans_under_qt(locale_folder, lang)
    # Many strings are translated at import time, so this is why we only import after the translator
    # has been installed
    from qt.app import MoneyGuru
    app.setApplicationVersion(MoneyGuru.VERSION)
    mgapp =  MoneyGuru()
    install_excepthook()
    exec_result = app.exec_()
    del mgapp
    # Since PyQt 4.7.2, I had crashes on exit, and from reading the mailing list, it seems to be
    # caused by some weird crap about C++ instance being deleted with python instance still living.
    # The worst part is that Phil seems to say this is expected behavior. So, whatever, this
    # gc.collect() below is required to avoid a crash.
    gc.collect()
    return exec_result

if __name__ == "__main__":
    sys.exit(main(sys.argv))
