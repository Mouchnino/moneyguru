# Created By: Virgil Dupras
# Created On: 2009-11-11
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtGui, QtCore

from hscommon.trans import trget

from ..support.date_edit import DateEdit
from .panel import Panel

tr = trget('ui')

class CustomDateRangePanel(Panel):
    FIELDS = [
        ('startDateEdit', 'start_date'),
        ('endDateEdit', 'end_date'),
        ('slotIndexComboBox', 'slot_index'),
        ('slotNameEdit', 'slot_name'),
    ]
    
    def __init__(self, mainwindow):
        Panel.__init__(self, mainwindow)
        self._setupUi()
        self.model = mainwindow.model.custom_daterange_panel
        self.model.view = self
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Custom Date Range"))
        self.resize(292, 86)
        self.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.label = QtGui.QLabel(tr("Select start and end dates from your custom range:"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.label_2 = QtGui.QLabel(tr("Start:"))
        self.horizontalLayout.addWidget(self.label_2)
        self.startDateEdit = DateEdit(self)
        self.horizontalLayout.addWidget(self.startDateEdit)
        self.label_3 = QtGui.QLabel(tr("End:"))
        self.horizontalLayout.addWidget(self.label_3)
        self.endDateEdit = DateEdit(self)
        self.horizontalLayout.addWidget(self.endDateEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.label_4 = QtGui.QLabel(tr("Save this range under slot:"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.slotIndexComboBox = QtGui.QComboBox(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slotIndexComboBox.sizePolicy().hasHeightForWidth())
        self.slotIndexComboBox.setSizePolicy(sizePolicy)
        for s in [tr("None"), tr("#1"), tr("#2"), tr("#3")]:
            self.slotIndexComboBox.addItem(s)
        self.horizontalLayout_2.addWidget(self.slotIndexComboBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.label_5 = QtGui.QLabel(tr("Under the name:"))
        self.horizontalLayout_3.addWidget(self.label_5)
        self.slotNameEdit = QtGui.QLineEdit(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slotNameEdit.sizePolicy().hasHeightForWidth())
        self.slotNameEdit.setSizePolicy(sizePolicy)
        self.horizontalLayout_3.addWidget(self.slotNameEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
