# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPixmap

from qtlib.column import Column
from ...support.item_delegate import ItemDecoration
from ..table import TableDelegate, DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT
from ..table_with_transactions import TableWithTransactions

class TransactionTableDelegate(TableDelegate):
    def __init__(self, model):
        TableDelegate.__init__(self, model)
        arrow = QPixmap(':/right_arrow_gray_12')
        arrowSelected = QPixmap(':/right_arrow_white_12')
        self._decoFromArrow = ItemDecoration(arrow, self._model.show_from_account)
        self._decoFromArrowSelected = ItemDecoration(arrowSelected, self._model.show_from_account)
        self._decoToArrow = ItemDecoration(arrow, self._model.show_to_account)
        self._decoToArrowSelected = ItemDecoration(arrowSelected, self._model.show_to_account)
    
    def _get_decorations(self, index, isSelected):
        column = self._model.columns.column_by_index(index.column())
        if column.name == 'from':
            return [self._decoFromArrowSelected if isSelected else self._decoFromArrow]
        elif column.name == 'to':
            return [self._decoToArrowSelected if isSelected else self._decoToArrow]
        else:
            return []
    

class TransactionTable(TableWithTransactions):
    COLUMNS = [
        Column('status', 25, cantTruncate=True),
        Column('date', 86, editor=DATE_EDIT, cantTruncate=True),
        Column('description', 230, editor=DESCRIPTION_EDIT),
        Column('payee', 150, editor=PAYEE_EDIT),
        Column('checkno', 80),
        Column('from', 120, editor=ACCOUNT_EDIT),
        Column('to', 120, editor=ACCOUNT_EDIT),
        Column('amount', 100, alignment=Qt.AlignRight, cantTruncate=True),
    ]
    
    def __init__(self, model, view):
        TableWithTransactions.__init__(self, model, view)
        self.tableDelegate = TransactionTableDelegate(self.model)
        self.view.setItemDelegate(self.tableDelegate)
        self.view.sortByColumn(1, Qt.AscendingOrder) # sorted by date by default
        self.view.deletePressed.connect(self.model.delete)
    
