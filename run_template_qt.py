#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import gc
import locale
import logging
import os
import os.path as op
import sip
sip.setapi('QVariant', 1)

from PyQt4.QtCore import QFile, QTextStream, QTranslator, QLocale, QSettings
from PyQt4.QtGui import QApplication, QIcon, QPixmap, QDesktopServices

import core.trans
from qtlib.error_report_dialog import install_excepthook
from qt.plat import LANG2LOCALENAME
import qt.mg_rc

def main(argv):
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(":/logo_small")))
    app.setOrganizationName('Hardcoded Software')
    app.setApplicationName('moneyGuru')
    appdata = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
    if not op.exists(appdata):
        os.makedirs(appdata)
    logging.basicConfig(filename=op.join(appdata, 'debug.log'), level=logging.WARNING)
    if sys.platform == 'linux2':
        stylesheetFile = QFile(':/stylesheet_lnx')
    else:
        stylesheetFile = QFile(':/stylesheet_win')
    stylesheetFile.open(QFile.ReadOnly)
    textStream = QTextStream(stylesheetFile)
    style = textStream.readAll()
    stylesheetFile.close()
    app.setStyleSheet(style)
    settings = QSettings()
    lang = str(settings.value('Language').toString())
    if not lang:
        lang = str(QLocale.system().name())[:2]
    if lang in LANG2LOCALENAME:
        # for date formatting
        localeName = LANG2LOCALENAME[lang]
        try:
            locale.setlocale(locale.LC_ALL, str(localeName))
        except locale.Error:
            logging.warning("Couldn't set locale %s", localeName)
        qtr1 = QTranslator()
        qtr1.load(':/qt_%s' % lang)
        app.installTranslator(qtr1)
        qtr2 = QTranslator()
        qtr2.load(':/%s' % lang)
        app.installTranslator(qtr2)
        def qt_tr(s, context='core'):
            return str(app.translate(context, s, None))
        core.trans.set_tr(qt_tr)
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