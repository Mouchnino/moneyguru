# Created By: Virgil Dupras
# Created On: 2009-12-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QSize
from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSizePolicy, QSpacerItem,
    QPushButton)

from hscommon.trans import tr as trbase
from core.gui.account_reassign_panel import AccountReassignPanel as AccountReassignPanelModel

from .. import plat
from .panel import Panel

tr = lambda s: trbase(s, "AccountReassignPanel")

class AccountReassignPanel(Panel):
    FIELDS = [
        ('accountComboBox', 'account_index'),
    ]
    
    def __init__(self, parent, mainwindow):
        Panel.__init__(self, parent)
        self._setupUi()
        self.model = AccountReassignPanelModel(view=self, mainwindow=mainwindow.model)
        
        self.continueButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
    
    def _setupUi(self):
        if plat.isWindows():
            self.resize(250, 140)
        else:
            self.resize(340, 165)
        self.setWindowTitle(tr("Re-assign Account"))
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setText(tr("You\'re about to delete a non-empty account. Select an account to re-assign its transactions to."))
        self.verticalLayout.addWidget(self.label)
        self.accountComboBox = QComboBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accountComboBox.sizePolicy().hasHeightForWidth())
        self.accountComboBox.setSizePolicy(sizePolicy)
        self.accountComboBox.setMinimumSize(QSize(200, 0))
        self.verticalLayout.addWidget(self.accountComboBox)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QHBoxLayout()
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cancelButton = QPushButton(self)
        self.cancelButton.setText(tr("Cancel"))
        self.cancelButton.setShortcut("Esc")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.continueButton = QPushButton(self)
        self.continueButton.setDefault(True)
        self.continueButton.setText(tr("Continue"))
        self.horizontalLayout.addWidget(self.continueButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
    
    def _loadFields(self):
        self._changeComboBoxItems(self.accountComboBox, self.model.available_accounts)
        Panel._loadFields(self)
    

if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication, QDialog
    app = QApplication([])
    dialog = QDialog(None)
    AccountReassignPanel._setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())