# Created By: Virgil Dupras
# Created On: 2009-11-04
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, QLabel,
    QLineEdit, QPlainTextEdit, QAbstractItemView, QSizePolicy, QSpacerItem, QPushButton,
    QDialogButtonBox, QIcon, QPixmap)

from hscommon.trans import tr as trbase
from core.gui.transaction_panel import TransactionPanel as TransactionPanelModel
from ..support.item_view import TableView
from ..support.date_edit import DateEdit
from ..support.completable_edit import PayeeEdit, DescriptionEdit

from .panel import Panel
from .split_table import SplitTable

tr = lambda s: trbase(s, "TransactionPanel")

class TransactionPanel(Panel):
    FIELDS = [
        ('dateEdit', 'date'),
        ('descriptionEdit', 'description'),
        ('payeeEdit', 'payee'),
        ('checkNoEdit', 'checkno'),
        ('notesEdit', 'notes'),
    ]
    
    def __init__(self, mainwindow):
        Panel.__init__(self, mainwindow)
        self.mainwindow = mainwindow
        self._setupUi()
        self.model = TransactionPanelModel(view=self, mainwindow=mainwindow.model)
        self.splitTable = SplitTable(model=self.model.split_table, view=self.splitTableView)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.mctButton.clicked.connect(self.model.mct_balance)
        self.addSplitButton.clicked.connect(self.splitTable.model.add)
        self.removeSplitButton.clicked.connect(self.splitTable.model.delete)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Transaction Info"))
        self.resize(462, 329)
        self.setModal(True)
        self.mainLayout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        self.infoTab = QWidget()
        self.infoLayout = QVBoxLayout(self.infoTab)
        self.formLayout = QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.dateEdit = DateEdit(self.infoTab)
        self.dateEdit.setMaximumSize(QSize(120, 16777215))
        self.formLayout.addRow(tr("Date:"), self.dateEdit)
        self.descriptionEdit = DescriptionEdit(self.infoTab)
        self.formLayout.addRow(tr("Description:"), self.descriptionEdit)
        self.payeeEdit = PayeeEdit(self.infoTab)
        self.formLayout.addRow(tr("Payee:"), self.payeeEdit)
        self.checkNoEdit = QLineEdit(self.infoTab)
        self.checkNoEdit.setMaximumSize(QSize(120, 16777215))
        self.formLayout.addRow(tr("Check #:"), self.checkNoEdit)
        self.infoLayout.addLayout(self.formLayout)
        self.amountLabel = QLabel(tr("Transfers:"), self.infoTab)
        self.infoLayout.addWidget(self.amountLabel)
        self.splitTableView = TableView(self.infoTab)
        self.splitTableView.setAcceptDrops(True)
        self.splitTableView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.splitTableView.setDragEnabled(True)
        self.splitTableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.splitTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.splitTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.splitTableView.horizontalHeader().setDefaultSectionSize(40)
        self.splitTableView.verticalHeader().setVisible(False)
        self.splitTableView.verticalHeader().setDefaultSectionSize(18)
        self.infoLayout.addWidget(self.splitTableView)
        self.mctButtonsLayout = QHBoxLayout()
        self.mctButtonsLayout.setMargin(0)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mctButtonsLayout.addItem(spacerItem)
        self.mctButton = QPushButton(tr("Multi-currency balance"), self.infoTab)
        self.mctButtonsLayout.addWidget(self.mctButton)
        self.addSplitButton = QPushButton(self.infoTab)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/plus_8"), QIcon.Normal, QIcon.Off)
        self.addSplitButton.setIcon(icon)
        self.mctButtonsLayout.addWidget(self.addSplitButton)
        self.removeSplitButton = QPushButton(self.infoTab)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/minus_8"), QIcon.Normal, QIcon.Off)
        self.removeSplitButton.setIcon(icon1)
        self.mctButtonsLayout.addWidget(self.removeSplitButton)
        self.infoLayout.addLayout(self.mctButtonsLayout)
        self.tabWidget.addTab(self.infoTab, tr("Info"))
        self.notesTab = QWidget()
        self.notesLayout = QVBoxLayout(self.notesTab)
        self.notesEdit = QPlainTextEdit(self.notesTab)
        self.notesLayout.addWidget(self.notesEdit)
        self.tabWidget.addTab(self.notesTab,  tr("Notes"))
        self.tabWidget.setCurrentIndex(0)
        self.mainLayout.addWidget(self.tabWidget)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.mainLayout.addWidget(self.buttonBox)
    
    def _loadFields(self):
        Panel._loadFields(self)
        self.tabWidget.setCurrentIndex(0)
    
    #--- model --> view
    def refresh_for_multi_currency(self):
        self.mctButton.setEnabled(self.model.is_multi_currency)
    

if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication, QDialog
    app = QApplication([])
    dialog = QDialog(None)
    TransactionPanel._setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())