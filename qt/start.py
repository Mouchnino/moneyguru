#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import gc

from PyQt4.QtCore import QFile, QTextStream
from PyQt4.QtGui import QApplication, QIcon, QPixmap

from qtlib.error_report_dialog import install_excepthook
from app import MoneyGuru

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(":/logo_small")))
    app.setOrganizationName('Hardcoded Software')
    app.setApplicationName('moneyGuru')
    app.setApplicationVersion(MoneyGuru.VERSION)
    if sys.platform == 'linux2':
        stylesheetFile = QFile(':/stylesheet_lnx')
    else:
        stylesheetFile = QFile(':/stylesheet_win')
    stylesheetFile.open(QFile.ReadOnly)
    textStream = QTextStream(stylesheetFile)
    style = textStream.readAll()
    stylesheetFile.close()
    app.setStyleSheet(style)
    mgapp = MoneyGuru()
    install_excepthook()
    exec_result = app.exec_()
    del mgapp
    # Since PyQt 4.7.2, I had crashes on exit, and from reading the mailing list, it seems to be
    # caused by some weird crap about C++ instance being deleted with python instance still living.
    # The worst part is that Phil seems to say this is expected behavior. So, whatever, this
    # gc.collect() below is required to avoid a crash.
    gc.collect()
    del app
    sys.exit(exec_result)
