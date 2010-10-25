# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtGui import QWidget

from ..ui.date_range_selector_view_ui import Ui_DateRangeSelectorView

class DateRangeSelectorView(QWidget, Ui_DateRangeSelectorView):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
    
