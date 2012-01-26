# Created By: Virgil Dupras
# Created On: 2009-11-29
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QAbstractTableModel
from PyQt4.QtGui import QWidget, QMenu, QCursor, QPixmap, QInputDialog, QMessageBox

from hscommon.trans import trget
from core.gui.csv_options import CSVOptions as CSVOptionsModel, FIELD_NAMES, FIELD_ORDER, \
    SUPPORTED_ENCODINGS

tr = trget('ui')

NEW_LAYOUT = 'new_layout'
RENAME_LAYOUT = 'rename_layout'
DELETE_LAYOUT = 'delete_layout'

class CSVOptionsWindow(QWidget):
    def __init__(self, parent, doc):
        QWidget.__init__(self, parent, Qt.Window)
        self._setupUi()
        self.doc = doc
        self.model = CSVOptionsModel(document=doc.model)
        self.tableModel = CSVOptionsTableModel(self.model, self.tableView)
        self.model.view = self
        self.encodingComboBox.addItems(SUPPORTED_ENCODINGS)
        
        self.cancelButton.clicked.connect(self.hide)
        self.continueButton.clicked.connect(self.model.continue_import)
        self.targetComboBox.currentIndexChanged.connect(self.targetIndexChanged)
        self.layoutComboBox.currentIndexChanged.connect(self.layoutIndexChanged)
        self.rescanButton.clicked.connect(self.rescanClicked)
    
    def _setupUi(self):
        self.setWindowTitle(tr("CSV Options"))
        self.resize(526, 369)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        msg = tr("Specify which CSV columns correspond to which transaction fields. You must also "
            "uncheck the \"Import\" column for lines that don\'t represent a transaction "
            "(header, footer, comments).")
        self.label = QtGui.QLabel(msg)
        self.label.setWordWrap(True)
        self.verticalLayout.addWidget(self.label)
        self.gridLayout = QtGui.QGridLayout()
        self.label_2 = QtGui.QLabel(tr("Layout:"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.layoutComboBox = QtGui.QComboBox(self)
        self.layoutComboBox.setMinimumSize(QtCore.QSize(160, 0))
        self.gridLayout.addWidget(self.layoutComboBox, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(tr("Delimiter:"))
        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1)
        self.fieldSeparatorEdit = QtGui.QLineEdit(self)
        self.fieldSeparatorEdit.setMaximumSize(QtCore.QSize(30, 16777215))
        self.gridLayout.addWidget(self.fieldSeparatorEdit, 0, 4, 1, 1)
        self.targetComboBox = QtGui.QComboBox(self)
        self.gridLayout.addWidget(self.targetComboBox, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(tr("Target:"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.encodingComboBox = QtGui.QComboBox(self)
        self.gridLayout.addWidget(self.encodingComboBox, 1, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.rescanButton = QtGui.QPushButton(tr("Rescan"))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rescanButton.sizePolicy().hasHeightForWidth())
        self.rescanButton.setSizePolicy(sizePolicy)
        self.horizontalLayout_2.addWidget(self.rescanButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 3, 1, 2)
        self.label_5 = QtGui.QLabel(tr("Encoding:"))
        self.gridLayout.addWidget(self.label_5, 1, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tableView = QtGui.QTableView(self)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setShowGrid(False)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.verticalLayout.addWidget(self.tableView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.cancelButton = QtGui.QPushButton(tr("Cancel"))
        self.cancelButton.setShortcut("Esc")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.continueButton = QtGui.QPushButton(tr("Continue Import"))
        self.continueButton.setDefault(True)
        self.horizontalLayout.addWidget(self.continueButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
    
    #--- Private
    def _newLayout(self):
        title = tr("New Layout")
        msg = tr("Choose a name for your new layout:")
        name, ok = QInputDialog.getText(self, title, msg)
        if ok and name:
            self.model.new_layout(name)
    
    def _renameLayout(self):
        title = tr("Rename Layout")
        msg = tr("Choose a name for your layout:")
        name, ok = QInputDialog.getText(self, title, msg)
        if ok and name:
            self.model.rename_selected_layout(name)
    
    #--- Event Handling
    def layoutIndexChanged(self, index):
        # This one is a little complicated. We want to only be able to select the layouts. If 
        # anything else is clicked, we revert back to the old index. If the item has user data,
        # it means that an action has to be performed.
        if index < 0:
            return
        elif index < len(self.model.layout_names):
            layout_name = None if index == 0 else str(self.layoutComboBox.itemText(index))
            self.model.select_layout(layout_name)
        else:
            self.layoutComboBox.setCurrentIndex(self.layoutComboBox.findText(self.model.layout.name))
            data = str(self.layoutComboBox.itemData(index).toString())
            if data == NEW_LAYOUT:
                self._newLayout()
            elif data == RENAME_LAYOUT:
                self._renameLayout()
            elif data == DELETE_LAYOUT:
                self.model.delete_selected_layout()
    
    def rescanClicked(self):
        self.model.encoding_index = self.encodingComboBox.currentIndex()
        self.model.field_separator = str(self.fieldSeparatorEdit.text())
        self.model.rescan()
    
    def targetIndexChanged(self, index):
        self.model.selected_target_index = index
    
    #--- model --> view
    # hide() is called from the model, but is already covered by QWidget
    def refresh_columns(self):
        self.tableModel.reset()
    
    def refresh_columns_name(self):
        self.tableModel.refreshColumnsName()
    
    def refresh_layout_menu(self):
        self.layoutComboBox.currentIndexChanged.disconnect(self.layoutIndexChanged)
        self.layoutComboBox.clear()
        self.layoutComboBox.addItems(self.model.layout_names)
        self.layoutComboBox.insertSeparator(self.layoutComboBox.count())
        self.layoutComboBox.addItem(tr("New Layout..."), NEW_LAYOUT)
        self.layoutComboBox.addItem(tr("Rename Selected Layout..."), RENAME_LAYOUT)
        self.layoutComboBox.addItem(tr("Delete Selected Layout"), DELETE_LAYOUT)
        self.layoutComboBox.setCurrentIndex(self.layoutComboBox.findText(self.model.layout.name))
        self.layoutComboBox.currentIndexChanged.connect(self.layoutIndexChanged)
    
    def refresh_lines(self):
        self.tableModel.reset()
        self.fieldSeparatorEdit.setText(self.model.field_separator)
    
    def refresh_targets(self):
        self.targetComboBox.currentIndexChanged.disconnect(self.targetIndexChanged)
        self.targetComboBox.clear()
        self.targetComboBox.addItems(self.model.target_account_names)
        self.targetComboBox.currentIndexChanged.connect(self.targetIndexChanged)
    
    def show(self):
        # For non-modal dialogs, show() is not enough to bring the window at the forefront, we have
        # to call raise() as well
        QWidget.show(self)
        self.raise_()
    
    def show_message(self, msg):
        title = "Warning"
        QMessageBox.warning(self, title, msg)
    

class CSVOptionsTableModel(QAbstractTableModel):
    def __init__(self, model, view):
        QAbstractTableModel.__init__(self)
        self.model = model
        self.view = view
        self.view.setModel(self)
        self._lastClickedColumn = 0
        self.columnMenu = QMenu()
        for index, fieldId in enumerate(FIELD_ORDER):
            fieldName = FIELD_NAMES[fieldId]
            action = self.columnMenu.addAction(fieldName)
            action.setData(index)
            action.triggered.connect(self.columnMenuItemClicked)
        self.view.horizontalHeader().sectionClicked.connect(self.tableSectionClicked)
    
    #--- QAbstractTableModel overrides
    # We add an additional "Import" column to the csv columns
    def columnCount(self, index):
        return len(self.model.columns) + 1
    
    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return None
            line = self.model.lines[index.row()]
            return line[index.column()-1]
        elif role == Qt.CheckStateRole and index.column() == 0:
            return Qt.Unchecked if self.model.line_is_excluded(index.row()) else Qt.Checked
        else:
            return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable
        return flags
    
    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal:
            return None
        if section > len(self.model.columns):
            return None
        if role == Qt.DisplayRole:
            if section == 0:
                return tr("Import")
            else:
                return self.model.get_column_name(section-1)
        elif role == Qt.DecorationRole and section > 0:
            return QPixmap(':/popup_arrows')
        else:
            return None
    
    def rowCount(self, index):
        if index.isValid():
            return 0
        return len(self.model.lines)
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole and index.column() == 0:
            self.model.set_line_excluded(index.row(), value == Qt.Unchecked)
            return True
        return False
    
    #--- Public
    def refreshColumnsName(self):
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(self.model.columns))
    
    #--- Event Handling
    def columnMenuItemClicked(self):
        action = self.sender()
        index, _ = action.data().toInt()
        fieldId = FIELD_ORDER[index]
        self.model.set_column_field(self._lastClickedColumn-1, fieldId)
    
    def tableSectionClicked(self, index):
        self._lastClickedColumn = index
        if index > 0:
            self.columnMenu.exec_(QCursor.pos())
