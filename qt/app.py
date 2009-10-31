# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.app import Application as MoneyGuruModel

from controller.document import Document
from controller.main_window import MainWindow

class MoneyGuru(object):
    VERSION = '1.6.7'
    def __init__(self):
        self.model = MoneyGuruModel(view=self)
        # on the Qt side, we're single document based, so it's one doc per app.
        self.doc = Document(app=self)
        self.mainWindow = MainWindow(doc=self.doc)
        self.mainWindow.show()
    
    # model --> view
    def get_default(self, key):
        return None
    
