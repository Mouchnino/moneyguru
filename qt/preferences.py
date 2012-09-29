# Created By: Virgil Dupras
# Created On: 2009-11-17
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op

from PyQt4.QtCore import QLocale
from PyQt4.QtGui import QApplication

from core.model.date import clean_format
from qtlib.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    def _load_values(self, settings):
        get = self.get_value
        self.recentDocuments = get('RecentDocuments', self.recentDocuments)
        self.recentDocuments = list(filter(op.exists, self.recentDocuments))
        self.dateFormat = get('DateFormat', self.dateFormat)
        self.tableFontSize = get('TableFontSize', self.tableFontSize)
        self.language = get('Language', self.language)
        
    def reset(self):
        locale = QLocale.system()
        self.recentDocuments = []
        dateFormat = str(locale.dateFormat(QLocale.ShortFormat))
        dateFormat = clean_format(dateFormat)
        self.dateFormat = dateFormat
        self.tableFontSize = QApplication.font().pointSize()
        self.language = ''
        
    def _save_values(self, settings):
        set_ = self.set_value
        set_('RecentDocuments', self.recentDocuments)
        set_('DateFormat', self.dateFormat)
        set_('TableFontSize', self.tableFontSize)
        set_('Language', self.language)
    
