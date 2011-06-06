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
        self.splitTable = SplitTable(transactionPanel=self, view=self.splitTableView)
        self.splitTable.model.connect()
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.mctButton.clicked.connect(self.model.mct_balance)
        self.addSplitButton.clicked.connect(self.splitTable.model.add)
        self.removeSplitButton.clicked.connect(self.splitTable.model.delete)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Transaction Info"))
        self.resize(462, 329)
        self.setModal(True)
        self.verticalLayout_2 = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        self.tab = QWidget()
        self.formLayout = QFormLayout(self.tab)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.label_2 = QLabel(tr("Date:"), self.tab)
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)
        self.dateEdit = DateEdit(self.tab)
        self.dateEdit.setMaximumSize(QSize(120, 16777215))
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.dateEdit)
        self.label_3 = QLabel(tr("Description:"), self.tab)
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_3)
        self.descriptionEdit = DescriptionEdit(self.tab)
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.descriptionEdit)
        self.label_4 = QLabel(tr("Payee:"), self.tab)
        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_4)
        self.payeeEdit = PayeeEdit(self.tab)
        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.payeeEdit)
        self.label_5 = QLabel(tr("Check #:"), self.tab)
        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_5)
        self.checkNoEdit = QLineEdit(self.tab)
        self.checkNoEdit.setMaximumSize(QSize(120, 16777215))
        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.checkNoEdit)
        self.amountLabel = QLabel(tr("Transfers:"), self.tab)
        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.amountLabel)
        self.splitTableView = TableView(self.tab)
        self.splitTableView.setMinimumSize(QSize(355, 0))
        self.splitTableView.setAcceptDrops(True)
        self.splitTableView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.splitTableView.setDragEnabled(True)
        self.splitTableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.splitTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.splitTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.splitTableView.horizontalHeader().setDefaultSectionSize(40)
        self.splitTableView.verticalHeader().setVisible(False)
        self.splitTableView.verticalHeader().setDefaultSectionSize(18)
        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.splitTableView)
        self.widget = QWidget(self.tab)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.mctButton = QPushButton(tr("Multi-currency balance"), self.widget)
        self.horizontalLayout.addWidget(self.mctButton)
        self.addSplitButton = QPushButton(self.widget)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/plus_8"), QIcon.Normal, QIcon.Off)
        self.addSplitButton.setIcon(icon)
        self.horizontalLayout.addWidget(self.addSplitButton)
        self.removeSplitButton = QPushButton(self.widget)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/minus_8"), QIcon.Normal, QIcon.Off)
        self.removeSplitButton.setIcon(icon1)
        self.horizontalLayout.addWidget(self.removeSplitButton)
        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.widget)
        self.tabWidget.addTab(self.tab, tr("Info"))
        self.tab_3 = QWidget()
        self.verticalLayout_3 = QVBoxLayout(self.tab_3)
        self.notesEdit = QPlainTextEdit(self.tab_3)
        self.verticalLayout_3.addWidget(self.notesEdit)
        self.tabWidget.addTab(self.tab_3,  tr("Notes"))
        self.tabWidget.setCurrentIndex(0)
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.label_2.setBuddy(self.dateEdit)
        self.label_3.setBuddy(self.descriptionEdit)
        self.label_4.setBuddy(self.payeeEdit)
        self.label_5.setBuddy(self.checkNoEdit)
    
    def _loadFields(self):
        Panel._loadFields(self)
        self.tabWidget.setCurrentIndex(0)
    
    #--- model --> view
    def refresh_for_multi_currency(self):
        self.mctButton.setEnabled(self.model.is_multi_currency)
    
