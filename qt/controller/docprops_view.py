# Created On: 2011/10/13
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtGui import QFormLayout, QComboBox

from hscommon.trans import tr as trbase
from qtlib.selectable_list import ComboboxModel
from core.gui.docprops_view import DocPropsView as DocPropsViewModel

from .base_view import BaseView

tr = lambda s: trbase(s, "DocPropsView")

class DocPropsView(BaseView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self._setupUi()
        self.model = DocPropsViewModel(view=self, mainwindow=mainwindow.model)
        self.currencyComboBox = ComboboxModel(model=self.model.currency_list, view=self.currencyComboBoxView)
        self.firstWeekdayComboBox = ComboboxModel(model=self.model.first_weekday_list,
            view=self.firstWeekdayComboBoxView)
        self.aheadMonthsComboBox = ComboboxModel(model=self.model.ahead_months_list,
            view=self.aheadMonthsComboBoxView)
        self.yearStartComboBox = ComboboxModel(model=self.model.year_start_month_list,
            view=self.yearStartComboBoxView)
    
    def _setupUi(self):
        self.mainLayout = QFormLayout(self)
        
        self.currencyComboBoxView = QComboBox()
        self.currencyComboBoxView.setEditable(True)
        self.currencyComboBoxView.setInsertPolicy(QComboBox.NoInsert)
        self.mainLayout.addRow(tr("Native Currency:"), self.currencyComboBoxView)
        
        self.firstWeekdayComboBoxView = QComboBox(self)
        self.mainLayout.addRow(tr("First day of the week:"), self.firstWeekdayComboBoxView)
        
        self.aheadMonthsComboBoxView = QComboBox(self)
        self.mainLayout.addRow(tr("Ahead months in Running Year:"), self.aheadMonthsComboBoxView)
        
        self.yearStartComboBoxView = QComboBox(self)
        self.mainLayout.addRow(tr("Year starts in:"), self.yearStartComboBoxView)
        