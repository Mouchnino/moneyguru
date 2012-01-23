# Created By: Virgil Dupras
# Created On: 2009-12-10
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from hscommon.trans import trget

from core.document import ScheduleScope

tr = trget('ui')

class ScheduleScopeDialog(QDialog):
    def __init__(self, parent=None):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self._setupUi()
        self._result = ScheduleScope.Local
        
        self.cancelButton.clicked.connect(self.cancelClicked)
        self.globalScopeButton.clicked.connect(self.globalScopeClicked)
        self.localScopeButton.clicked.connect(self.localScopeClicked)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Schedule Modification Scope"))
        self.resize(333, 133)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.label = QtGui.QLabel(tr("Do you want this change to affect all future occurrences of this schedule?"))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(tr("You can force global scope (in other words, changing all future occurrences) by holding Shift when you perform the change."))
        self.label_2.setWordWrap(True)
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.cancelButton = QtGui.QPushButton(tr("Cancel"))
        self.cancelButton.setShortcut("Esc")
        self.horizontalLayout.addWidget(self.cancelButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.globalScopeButton = QtGui.QPushButton(tr("All future occurrences"))
        self.globalScopeButton.setAutoDefault(False)
        self.horizontalLayout.addWidget(self.globalScopeButton)
        self.localScopeButton = QtGui.QPushButton(tr("Just this one"))
        self.localScopeButton.setAutoDefault(False)
        self.localScopeButton.setDefault(True)
        self.horizontalLayout.addWidget(self.localScopeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
    
    def cancelClicked(self):
        self._result = ScheduleScope.Cancel
        self.accept()
    
    def globalScopeClicked(self):
        self._result = ScheduleScope.Global
        self.accept()
    
    def localScopeClicked(self):
        self._result = ScheduleScope.Local
        self.accept()
    
    def queryForScope(self):
        self.exec_()
        return self._result
    
