# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from qtlib.table import Table as TableBase

from ..support.completable_edit import DescriptionEdit, PayeeEdit, AccountEdit
from ..support.date_edit import DateEdit
from ..support.item_delegate import ItemDelegate

DATE_EDIT = 'date_edit'
DESCRIPTION_EDIT = 'description_edit'
PAYEE_EDIT = 'payee_edit'
ACCOUNT_EDIT = 'account_edit'

EDIT_TYPE2COMPLETABLE_EDIT = {
    DESCRIPTION_EDIT: DescriptionEdit,
    PAYEE_EDIT: PayeeEdit,
    ACCOUNT_EDIT: AccountEdit
}

class TableDelegate(ItemDelegate):
    def __init__(self, model):
        ItemDelegate.__init__(self)
        self._model = model
    
    def createEditor(self, parent, option, index):
        column = self._model.columns.column_by_index(index.column())
        editType = column.editor
        if editType is None:
            return ItemDelegate.createEditor(self, parent, option, index)
        elif editType == DATE_EDIT:
            return DateEdit(parent)
        elif editType in EDIT_TYPE2COMPLETABLE_EDIT:
            return EDIT_TYPE2COMPLETABLE_EDIT[editType](self._model.completable_edit, parent)
    

class Table(TableBase):
    def __init__(self, model, view):
        TableBase.__init__(self, model, view)
        self.tableDelegate = TableDelegate(self.model)
        self.view.setItemDelegate(self.tableDelegate)
