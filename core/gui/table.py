# Created By: Eric Mc Sween
# Created On: 2008-05-29
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime

class Table(list):
    def __init__(self):
        list.__init__(self)
        self._selected_indexes = []
    
    def __delitem__(self, key):
        list.__delitem__(self, key)
        self._check_selection_range()
    
    # this method is deprecated, but when subclassing list, we *have* to override it.
    def __delslice__(self, i, j):
        self.__delitem__(slice(i, j))
    
    def __eq__(self, other):
        # object doesn't have __eq__ and __cmp__ doesn't work
        return self is other
    
    def __hash__(self):
        return object.__hash__(self)
    
    def _check_selection_range(self):
        if not self:
            self._selected_indexes = []
        had_selection = bool(self._selected_indexes)
        self._selected_indexes = [index for index in self._selected_indexes if index < len(self)]
        if had_selection and not self._selected_indexes:
            self._selected_indexes.append(len(self) - 1)
    
    def remove(self, row):
        list.remove(self, row)
        self._check_selection_range()
    
    def sort(self, *args, **kwargs):
        raise NotImplementedError()
    
    @property
    def selected_row(self):
        return self[self.selected_index] if self.selected_index is not None else None
    
    @selected_row.setter
    def selected_row(self, value):
        try:
            self.selected_index = self.index(value)
        except ValueError:
            pass
    
    @property
    def selected_rows(self):
        return [self[index] for index in self.selected_indexes]
    
    @property
    def selected_index(self):
        return self._selected_indexes[0] if self._selected_indexes else None
    
    @selected_index.setter
    def selected_index(self, value):
        self.selected_indexes = [value]
    
    @property
    def selected_indexes(self):
        return self._selected_indexes
    
    @selected_indexes.setter
    def selected_indexes(self, value):
        self._selected_indexes = value
        self._selected_indexes.sort()
        self._check_selection_range()
    

# Subclasses of this class must have a "view" and a "document" attribute
class GUITable(Table):
    def __init__(self):
        Table.__init__(self)
        self.edited = None
    
    #--- Virtual
    def _do_add(self):
        # Creates a new row, adds it in the table and returns it.
        return None
    
    def _do_delete(self):
        # Delete the selected rows
        pass
    
    def _fill(self):
        # Called by refresh()
        # Fills the table with all the rows that this table is supposed to have.
        pass
    
    def _is_edited_new(self):
        return False
    
    def _update_selection(self):
        # Takes the table's selection and does appropriates updates on the Document's side.
        pass
    
    #--- Public
    def add(self):
        self.view.stop_editing()
        if self.edited is not None:
            self.save_edits()
        row = self._do_add()
        assert row is not None
        self.edited = row
        self.view.refresh()
        self.view.start_editing()
    
    def can_edit_cell(self, column_name, row_index):
        # A row is, by default, editable as soon as it has an attr with the same name as `column`.
        # If can_edit() returns False, the row is not editable at all. You can set editability of
        # rows at the attribute level with can_edit_* properties
        row = self[row_index]
        return row.can_edit_cell(column_name)
    
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
    
    def cancel_edits(self):
        if self.edited is None:
            return
        self.view.stop_editing()
        if self._is_edited_new():
            self.remove(self.edited)
            self._update_selection()
        else:
            self.edited.load()
        self.edited = None
        self.view.refresh()
    
    def delete(self):
        self.view.stop_editing()
        if self.edited is not None:
            self.cancel_edits()
            return
        if self:
            self._do_delete()
    
    def refresh(self):
        self.cancel_edits()
        selected_indexes = self.selected_indexes
        del self[:]
        self._fill()
        if not self.selected_indexes:
            if not selected_indexes:
                selected_indexes = [len(self) - 1]
            self.select(selected_indexes)
    
    def save_edits(self):
        if self.edited is None:
            return
        row = self.edited
        self.edited = None
        row.save()
    
    def select(self, row_indexes):
        self.selected_indexes = row_indexes
        self._update_selection()
    
    #--- Event handlers
    def edition_must_stop(self):
        self.view.stop_editing()
        self.save_edits()
    
    def document_changed(self):
        self.refresh()
        self.view.refresh()
    
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
    

class Row(object):
    def __init__(self, table):
        super(Row, self).__init__()
        self.table = table
    
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
        columns = self.table._columns
        if columns:
            column_index = columns.index(key_attr)
            right_columns = set(columns[column_index + 1:])
            return set(all_attrs) & right_columns
        else:
            return set(all_attrs)
    
    def _get_autofill_rows(self):
        # generator
        raise NotImplementedError()
    
    def _edit(self):
        if self.table.edited is self:
            return
        assert self.table.edited is None
        self.table.edited = self
    
    #--- Virtual
    def can_edit(self):
        return True
    
    def load(self):
        raise NotImplementedError()
    
    def save(self):
        raise NotImplementedError()
    
    #--- Public
    def can_edit_cell(self, column_name):
        if not self.can_edit():
            return False
        # '_' is in case column is a python keyword
        if not (hasattr(self, column_name) or hasattr(self, column_name + '_')):
            return False
        return getattr(self, 'can_edit_' + column_name, True)
    

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
        self.table.stop_completion()
    
    return property(fget, fset)
    
