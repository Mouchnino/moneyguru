# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtCore, QtGui

from hscommon.currency import Currency
from hscommon.trans import trget
from qtlib.selectable_list import ComboboxModel
from qtlib.text_field import TextField

from ..support.date_edit import DateEdit
from ..support.completable_edit import PayeeEdit, AccountEdit, DescriptionEdit
from .panel import Panel

tr = trget('ui')

class MassEditionPanel(Panel):
    FIELDS = [
        ('dateCheckBox', 'date_enabled'),
        ('descriptionCheckBox', 'description_enabled'),
        ('payeeCheckBox', 'payee_enabled'),
        ('checknoCheckBox', 'checkno_enabled'),
        ('fromCheckBox', 'from_enabled'),
        ('toCheckBox', 'to_enabled'),
        ('amountCheckBox', 'amount_enabled'),
        ('currencyCheckBox', 'currency_enabled'),
    ]
    
    def __init__(self, mainwindow):
        Panel.__init__(self, mainwindow)
        self.mainwindow = mainwindow
        self.model = mainwindow.model.mass_edit_panel
        self._setupUi()
        self.model.view = self
        self.dateEdit = TextField(model=self.model.date_field, view=self.dateEditView)
        self.descriptionEdit = TextField(model=self.model.description_field, view=self.descriptionEditView)
        self.payeeEdit = TextField(model=self.model.payee_field, view=self.payeeEditView)
        self.checknoEdit = TextField(model=self.model.checkno_field, view=self.checknoEditView)
        self.fromEdit = TextField(model=self.model.from_field, view=self.fromEditView)
        self.toEdit = TextField(model=self.model.to_field, view=self.toEditView)
        self.amountEdit = TextField(model=self.model.amount_field, view=self.amountEditView)
        self.currencyComboBox = ComboboxModel(model=self.model.currency_list, view=self.currencyComboBoxView)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        self.resize(314, 267)
        self.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.label = QtGui.QLabel(tr("Date:"), self)
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.dateCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout.addWidget(self.dateCheckBox)
        self.dateEditView = DateEdit(self)
        self.horizontalLayout.addWidget(self.dateEditView)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_2 = QtGui.QLabel(tr("Description:"), self)
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.descriptionCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout_2.addWidget(self.descriptionCheckBox)
        self.descriptionEditView = DescriptionEdit(self.model.completable_edit, self)
        self.horizontalLayout_2.addWidget(self.descriptionEditView)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.label_3 = QtGui.QLabel(tr("Payee:"), self)
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.payeeCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout_3.addWidget(self.payeeCheckBox)
        self.payeeEditView = PayeeEdit(self.model.completable_edit, self)
        self.horizontalLayout_3.addWidget(self.payeeEditView)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.label_4 = QtGui.QLabel(tr("Check #"), self)
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.checknoCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout_4.addWidget(self.checknoCheckBox)
        self.checknoEditView = QtGui.QLineEdit(self)
        self.horizontalLayout_4.addWidget(self.checknoEditView)
        self.formLayout.setLayout(3, QtGui.QFormLayout.FieldRole, self.horizontalLayout_4)
        self.label_5 = QtGui.QLabel(tr("From:"), self)
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_5)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.fromCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout_5.addWidget(self.fromCheckBox)
        self.fromEditView = AccountEdit(self.model.completable_edit, self)
        self.horizontalLayout_5.addWidget(self.fromEditView)
        self.formLayout.setLayout(4, QtGui.QFormLayout.FieldRole, self.horizontalLayout_5)
        self.label_6 = QtGui.QLabel(tr("To:"), self)
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_6)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.toCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout_6.addWidget(self.toCheckBox)
        self.toEditView = AccountEdit(self.model.completable_edit, self)
        self.horizontalLayout_6.addWidget(self.toEditView)
        self.formLayout.setLayout(5, QtGui.QFormLayout.FieldRole, self.horizontalLayout_6)
        self.label_7 = QtGui.QLabel(tr("Amount:"), self)
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.label_7)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.amountCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout_7.addWidget(self.amountCheckBox)
        self.amountEditView = QtGui.QLineEdit(self)
        self.horizontalLayout_7.addWidget(self.amountEditView)
        self.formLayout.setLayout(6, QtGui.QFormLayout.FieldRole, self.horizontalLayout_7)
        self.label_8 = QtGui.QLabel(tr("Currency:"), self)
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.label_8)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.currencyCheckBox = QtGui.QCheckBox(self)
        self.horizontalLayout_8.addWidget(self.currencyCheckBox)
        self.currencyComboBoxView = QtGui.QComboBox(self)
        self.currencyComboBoxView.setEditable(True)
        self.horizontalLayout_8.addWidget(self.currencyComboBoxView)
        self.formLayout.setLayout(7, QtGui.QFormLayout.FieldRole, self.horizontalLayout_8)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.dateEditView)
        self.label_2.setBuddy(self.descriptionEditView)
        self.label_3.setBuddy(self.payeeEditView)
        self.label_4.setBuddy(self.checknoEditView)
        self.label_5.setBuddy(self.fromEditView)
        self.label_6.setBuddy(self.toEditView)
        self.label_7.setBuddy(self.amountEditView)
        self.label_8.setBuddy(self.currencyComboBoxView)
    
    def _loadFields(self):
        Panel._loadFields(self)
        disableableWidgets = [self.fromCheckBox, self.fromEdit, self.toCheckBox, self.toEdit]
        for widget in disableableWidgets:
            self.fromCheckBox.setEnabled(self.model.can_change_accounts)
        disableableWidgets = [self.amountCheckBox, self.amountEdit]
        for widget in disableableWidgets:
            self.fromCheckBox.setEnabled(self.model.can_change_amount)
    
    #--- model --> view
    def refresh(self):
        # We have to refresh the checkboxes' state.
        self._loadFields()
    
