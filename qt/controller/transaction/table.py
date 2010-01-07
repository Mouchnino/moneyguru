# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPixmap

from core.gui.transaction_table import TransactionTable as TransactionTableModel
from support.item_delegate import ItemDecoration
from ..column import Column, DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT
from ..table import TableDelegate
from ..table_with_transactions import TableWithTransactions

# XXX The totals label is tied to the table, even in the model. This is a design flaw. The totals
# label should be an independent gui element (or be a part of an eventual new transaction_view gui
# element).

class TransactionTableDelegate(TableDelegate):
    def __init__(self, model, columns):
        TableDelegate.__init__(self, model, columns)
        arrow = QPixmap(':/right_arrow_gray_12')
        arrowSelected = QPixmap(':/right_arrow_white_12')
        self._decoFromArrow = ItemDecoration(arrow, self._model.show_from_account)
        self._decoFromArrowSelected = ItemDecoration(arrowSelected, self._model.show_from_account)
        self._decoToArrow = ItemDecoration(arrow, self._model.show_to_account)
        self._decoToArrowSelected = ItemDecoration(arrowSelected, self._model.show_to_account)
    
    def _get_decorations(self, index, isSelected):
        column = self._columns[index.column()]
        if column.attrname == 'from_':
            return [self._decoFromArrowSelected if isSelected else self._decoFromArrow]
        elif column.attrname == 'to':
            return [self._decoToArrowSelected if isSelected else self._decoToArrow]
        else:
            return []
    

class TransactionTable(TableWithTransactions):
    COLUMNS = [
        Column('status', '', 25),
        Column('date', 'Date', 86, editor=DATE_EDIT),
        Column('description', 'Description', 230, editor=DESCRIPTION_EDIT),
        Column('payee', 'Payee', 150, editor=PAYEE_EDIT),
        Column('checkno', 'Check #', 80),
        Column('from_', 'From', 120, editor=ACCOUNT_EDIT),
        Column('to', 'To', 120, editor=ACCOUNT_EDIT),
        Column('amount', 'Amount', 100, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, doc, view, totalsLabel):
        model = TransactionTableModel(view=self, document=doc.model)
        TableWithTransactions.__init__(self, model, view)
        self.tableDelegate = TransactionTableDelegate(self.model, self.COLUMNS)
        self.view.setItemDelegate(self.tableDelegate)
        self.totalsLabel = totalsLabel
        self.view.sortByColumn(1, Qt.AscendingOrder) # sorted by date by default
        self.view.horizontalHeader().sectionMoved.connect(self.headerSectionMoved)
        self.view.deletePressed.connect(self.model.delete)
    
    #--- ColumnBearer override
    def setHiddenColumns(self, hiddenColumns):
        # There doesn't seem to be a signal for column hide. Since we only hide column through this
        # call, we can call change_columns() here.
        TableWithTransactions.setHiddenColumns(self, hiddenColumns)
        self.model.change_columns(self.visibleRowAttrs())
    
    #--- Event Handling
    def headerSectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        self.model.change_columns(self.visibleRowAttrs())
    
    #--- model --> view
    def refresh(self):
        TableWithTransactions.refresh(self)
        self.totalsLabel.setText(self.model.totals)
    
