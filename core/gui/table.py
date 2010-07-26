# Created By: Eric Mc Sween
# Created On: 2008-05-29
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime

from hsgui.table import Table, GUITable as GUITableBase, Row as RowBase

from ..model.amount import Amount
from ..model.sort import sort_string
from .column import Columns

# Subclasses of this class must have a "view" and a "document" attribute
class GUITable(GUITableBase):
    SAVENAME = ''
    ALL_ATTRS = []
    
    def __init__(self):
        GUITableBase.__init__(self)
        self.columns = Columns(self.document.app, self.SAVENAME, self.ALL_ATTRS)
    
    def can_move(self, row_indexes, position):
        if not 0 <= position <= len(self):
            return False
        row_indexes.sort()
        first_index = row_indexes[0]
        last_index = row_indexes[-1]
        has_gap = row_indexes != range(first_index, first_index + len(row_indexes))
        # When there is a gap, position can be in the middle of row_indexes
        if not has_gap and position in (row_indexes + [last_index + 1]):
            return False
        return True
    
    #--- Event handlers
    def edition_must_stop(self):
        self.view.stop_editing()
        self.save_edits()
    
    def document_changed(self):
        self.refresh()
        self.view.refresh()
    
    def document_will_close(self):
        self.columns.save_columns()
    
    def performed_undo_or_redo(self):
        self.refresh()
        self.view.refresh()
    
    # Plug these below to the appropriate event in subclasses
    def _filter_applied(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
    
    def _item_changed(self):
        self.refresh()
        self.view.refresh()
        self.view.show_selected_row()
    
    def _item_deleted(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
    

class Row(RowBase):
    def _autofill(self, key_value, key_attr):
        if not key_value:
            return # we never autofill on blank values
        dest_attrs = self._get_autofill_dest_attrs(key_attr, self._get_autofill_attrs())
        if not dest_attrs:
            return
        # the attrs we set are the private ones because the public ones are formatted (bool('0.00') == True)
        key_attr = '_' + key_attr
        dest_attrs = set('_' + attrname for attrname in dest_attrs)
        for row in self._get_autofill_rows():
            if getattr(row, key_attr) == key_value:
                self._autofill_row(row, dest_attrs)
                break
    
    def _autofill_row(self, ref_row, dest_attrs):
        for attrname in dest_attrs:
            if not getattr(self, attrname):
                setattr(self, attrname, getattr(ref_row, attrname))
    
    def _get_autofill_attrs(self):
        raise NotImplementedError()
    
    def _get_autofill_dest_attrs(self, key_attr, all_attrs):
        """Returns a set of attrs to fill depending on which columns are right to key_attr
        """
        if self.table.columns.colnames:
            right_columns = set(self.table.columns.columns_to_right(key_attr))
            return set(all_attrs) & right_columns
        else:
            return set(all_attrs)
    
    def _get_autofill_rows(self):
        # generator
        raise NotImplementedError()
    
    #--- Override
    def sort_key_for_column(self, column_name):
        value = RowBase.sort_key_for_column(self, column_name)
        if isinstance(value, basestring):
            value = sort_string(value)
        elif isinstance(value, Amount):
            value = value.value
        return value
    

class RowWithDebitAndCredit(Row):
    @property
    def _debit(self):
        return self._amount if self._amount > 0 else 0
    
    @_debit.setter
    def _debit(self, debit):
        self._edit()
        if debit or self._debit:
            self._amount = debit
    
    @property
    def _credit(self):
        return -self._amount if self._amount < 0 else 0

    @_credit.setter
    def _credit(self, credit):
        self._edit()
        if credit or self._credit:
            self._amount = -credit
    
    @property
    def _decrease(self):
        return self._debit if self.account.is_credit_account() else self._credit
    
    @_decrease.setter
    def _decrease(self, decrease):
        self._edit()
        if self.account.is_credit_account():
            self._debit = decrease
        else:
            self._credit = decrease
    
    @property
    def _increase(self):
        return self._credit if self.account.is_credit_account() else self._debit
    
    @_increase.setter
    def _increase(self, increase):
        self._edit()
        if self.account.is_credit_account():
            self._credit = increase
        else:
            self._debit = increase
    

class RowWithDate(Row):
    def __init__(self, table):
        super(RowWithDate, self).__init__(table)
        self._date = datetime.date.today()
        self._date_fmt = None
    
    def is_date_in_future(self):
        return self._date > self.table.document.date_range.end
    
    def is_date_in_past(self):
        return self._date < self.table.document.date_range.start
    
    @property
    def date(self):
        if self._date_fmt is None:
            self._date_fmt = self.table.document.app.format_date(self._date)
        return self._date_fmt
    
    @date.setter
    def date(self, value):
        parsed = self.table.document.app.parse_date(value)
        if parsed == self._date:
            return
        self._edit()
        self._date = parsed
        self._date_fmt = None
    

def rowattr(attrname, autofillname=None):
    def fget(self):
        return getattr(self, attrname)
    
    def fset(self, value):
        old = getattr(self, attrname)
        if value == old:
            return
        self._edit()
        setattr(self, attrname, value)
        if autofillname:
            self._autofill(value, autofillname)
    
    return property(fget, fset)
    
