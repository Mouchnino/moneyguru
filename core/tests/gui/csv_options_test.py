# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-01-18
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..base import TestCase, Document, DocumentGUI, ApplicationGUI
from ...app import Application
from ...gui.csv_options import LAYOUT_PREFERENCE_NAME
from ...loader.csv import CsvField

class NoSetup(TestCase):
    def test_invalid_default(self):
        self.app_gui = ApplicationGUI()
        self.app_gui.defaults[LAYOUT_PREFERENCE_NAME] = 'invalid'
        self.app = Application(self.app_gui)
        self.create_instances() # no crash when CSVOptions is created
    

class ImportFortisCSV(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        expected_calls = ['refresh_layout_menu', 'refresh_columns', 'refresh_lines',
            'refresh_targets', 'show']
        self.check_gui_calls(self.csvopt_gui, expected_calls)
    
    def test_columns(self):
        eq_(self.csvopt.columns, [None] * 8)
    
    def test_continue_import(self):
        # because the columns haven't been set, the iwin is not supposed to be brought and an error
        # message is supposed to pop.
        self.csvopt.continue_import()
        self.check_gui_calls_partial(self.iwin_gui, not_expected=['show'])
        self.check_gui_calls(self.csvopt_gui, ['show_message'])
    
    def test_delete_selected_layout(self):
        # There used to be an assert in delete_selected_layout to make sure the default layout was
        # never deleted, but on PyQt, there doesn't seem to be an easy way to disable a menu item
        # in a combobox, so we'll just make delete_selected_layout do nothing.
        self.csvopt.delete_selected_layout() # do nothing, no assertion error
        eq_(self.csvopt.layout_names, ['Default'])
    
    def test_exclude_first_line(self):
        self.csvopt.set_line_excluded(0, True)
        assert self.csvopt.line_is_excluded(0)
    
    def test_get_column_name(self):
        eq_(self.csvopt.get_column_name(3), 'None')
    
    def test_lines(self):
        eq_(len(self.csvopt.lines), 19)
    
    def test_set_column_field(self):
        self.csvopt.set_column_field(1, CsvField.Date)
        eq_(self.csvopt.get_column_name(1), 'Date')
        self.check_gui_calls(self.csvopt_gui, ['refresh_columns_name'])
    

class ImportFortisCSVWithWrongDateColumn(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        self.csvopt.set_column_field(5, CsvField.Date) #description
        self.csvopt.set_column_field(3, CsvField.Amount)
        self.clear_gui_calls()
    
    def test_dont_change_line_values(self):
        # Continuing the import hasn't change the values of the lines.
        previous_value = self.csvopt.lines[2][5]
        self.csvopt.continue_import()
        eq_(self.csvopt.lines[2][5], previous_value)
    
    def test_show_error_message(self):
        # if the field date is set to a non-date column, raise an appropriate error (with show_message)
        self.csvopt.continue_import()
        self.check_gui_calls(self.csvopt_gui, ['show_message'])
    

class ImportFortisCSVWithoutFirstLineAndWithFieldsSet(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        self.csvopt.set_line_excluded(0, True)
        self.csvopt.set_column_field(0, CsvField.Reference)
        self.csvopt.set_column_field(1, CsvField.Date)
        self.csvopt.set_column_field(3, CsvField.Amount)
        self.csvopt.set_column_field(5, CsvField.Description)
        self.clear_gui_calls()
    
    def test_continue_import(self):
        # sets the columns in self.document.loader and continues importing
        self.csvopt.continue_import()
        self.check_gui_calls(self.csvopt_gui, ['hide'])
        self.check_gui_calls(self.iwin_gui, ['refresh_tabs', 'refresh_target_accounts', 'show'])
        eq_(len(self.iwin.panes), 1)
        eq_(self.iwin.panes[0].name, 'CSV Import')
        eq_(self.iwin.panes[0].count, 18)
        eq_(len(self.itable), 18)
        eq_(self.itable[0].date_import, '01/12/2008')
        eq_(self.itable[0].description_import, 'RETRAIT A UN DISTRIBUTEUR FORTIS')
        eq_(self.itable[0].amount_import, '-100.00')
    
    def test_continue_import_without_the_first_line_being_excluded(self):
        # When the user forgets to exclude a header line, just ignore that line in guess_date_format()
        self.csvopt.set_line_excluded(0, False)
        self.csvopt.continue_import()
        eq_(len(self.itable), 18)
        eq_(self.itable[0].date_import, '01/12/2008')
    
    def test_layouts(self):
        self.csvopt.new_layout('foobar') # 'foobar' is selected
        self.check_gui_calls(self.csvopt_gui, ['refresh_layout_menu'])
        eq_(self.csvopt.layout_names, ['Default', 'foobar'])
        self.csvopt.set_column_field(5, CsvField.Payee)
        self.clear_gui_calls()
        self.csvopt.select_layout(None) # default
        self.check_gui_calls(self.csvopt_gui, ['refresh_columns_name', 'refresh_lines', 'refresh_targets'])
        eq_(self.csvopt.columns[5], CsvField.Description)
        self.csvopt.select_layout('foobar')
        eq_(self.csvopt.columns[5], CsvField.Payee)
    
    def test_new_layout_with_empty_name(self):
        # when trying to add a layout with an empty name, do nothing
        self.csvopt.new_layout('')
        self.csvopt.new_layout(None)
        eq_(len(self.csvopt.layout_names), 1)
    
    def test_rename_layout_with_empty_name(self):
        # when trying to add a layout with an empty name, do nothing
        self.csvopt.rename_selected_layout('')
        self.csvopt.rename_selected_layout(None)
        eq_(self.csvopt.layout.name, 'Default')
    
    def test_set_same_field_on_another_column(self):
        # if a field is already set somewhere and that another column sets the same field elsewhere,
        # clear the other column
        self.csvopt.set_column_field(2, CsvField.Date)
        eq_(self.csvopt.get_column_name(1), 'None')
    

class LotsOfNoise(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/lots_of_noise.csv'))
    
    def test_use_latin1_encoding(self):
        # This file contains umlauts encoded in latin-1. Make sure they are correctly decoded
        s = self.csvopt.lines[0][0]
        assert isinstance(s, unicode)
        assert u'ä' in s
    

class LotsOfNoiseReadyToImport(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/lots_of_noise.csv'))
        self.csvopt.set_line_excluded(0, True)
        self.csvopt.set_line_excluded(1, True)
        self.csvopt.set_line_excluded(2, True)
        self.csvopt.set_line_excluded(3, True)
        self.csvopt.set_line_excluded(4, True)
        self.csvopt.set_line_excluded(7, True)
        self.csvopt.set_column_field(0, CsvField.Date)
        self.csvopt.set_column_field(2, CsvField.Description)
        self.csvopt.set_column_field(3, CsvField.Amount)
        self.clear_gui_calls()
    
    def test_continue_import(self):
        self.csvopt.continue_import()
        eq_(len(self.itable), 2)
        eq_(self.itable[0].date_import, '14/01/2009')
        eq_(self.itable[0].description_import, '1234512345123451 AMAZON.SER VICES S. 090114P3TX4612XG AMAZON.SERVICES S.A.R.L - E U-DE DR. THOMAS ECKHOLD')
        eq_(self.itable[0].amount_import, '-99.99')
    
    def test_load_fortis(self):
        # when loading another CSV, keep line exclusions that happen to be last *last*
        self.csvopt.set_line_excluded(6, True) # should also work for the line before the last
        self.csvopt.new_layout('fortis') # let's save it
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        self.csvopt.select_layout('fortis')
        assert not self.csvopt.line_is_excluded(6)
        assert not self.csvopt.line_is_excluded(7)
        assert self.csvopt.line_is_excluded(17)
        assert self.csvopt.line_is_excluded(18)
    
    def test_reinclude_last_line(self):
        # it's possible to re-include the last line. Previously, due to the negative index scheme,
        # it wouldn't be possible.
        self.csvopt.set_line_excluded(7, False)
        assert not self.csvopt.line_is_excluded(7)
    

class FortisWithTwoLayouts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_accounts('one', 'two', 'three')
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        self.csvopt.set_line_excluded(0, True)
        self.csvopt.set_column_field(0, CsvField.Reference)
        self.csvopt.set_column_field(1, CsvField.Date)
        self.csvopt.set_column_field(3, CsvField.Amount)
        self.csvopt.set_column_field(5, CsvField.Description)
        self.csvopt.new_layout('foobar') # 'foobar' is selected
        self.csvopt.selected_target_index = 1 # one
        self.csvopt.new_layout('foobaz') # 'foobaz' is selected
        self.csvopt.set_column_field(5, CsvField.Payee)
        self.clear_gui_calls()
    
    def test_close_document(self):
        # when the document is closed, layouts are saved to preferences
        self.document.close()
        # None values can't be in the preferences. They have to be replaced by empty strings.
        default = {
            'name': 'foobar',
            'columns': [CsvField.Reference, CsvField.Date, '', CsvField.Amount, '', CsvField.Description],
            'excluded_lines': [0],
            'target_account': 'one',
        }
        foobar = {
            'name': 'foobaz',
            'columns': [CsvField.Reference, CsvField.Date, '', CsvField.Amount, '', CsvField.Payee],
            'excluded_lines': [0]
        }
        eq_(self.app_gui.get_default(LAYOUT_PREFERENCE_NAME), [default, foobar])
    
    def test_delete_selected_layout(self):
        self.csvopt.delete_selected_layout()
        self.check_gui_calls(self.csvopt_gui, ['refresh_layout_menu', 'refresh_columns_name', 'refresh_lines'])
        eq_(self.csvopt.layout_names, ['Default', 'foobar'])
        eq_(self.csvopt.layout.name, 'Default')
    
    def test_load_another_import(self):
        # when a file is loaded, select the default layout, and reset it
        self.document.parse_file_for_import(self.filepath('csv/lots_of_noise.csv'))
        eq_(self.csvopt.layout.name, 'Default')
        assert self.csvopt.columns[5] is None
    
    def test_rename_selected_layout(self):
        self.csvopt.rename_selected_layout('foobaz')
        self.check_gui_calls(self.csvopt_gui, ['refresh_layout_menu'])
        eq_(self.csvopt.layout_names, ['Default', 'foobar', 'foobaz'])
    
    def test_rename_target_account(self):
        # When renaming an account targeted by a layout doesn't cause a crash next time this layout
        # is loaded.
        self.bsheet.selected = self.bsheet.assets[0] # 'one', the target account
        self.bsheet.assets[0].name = 'renamed'
        self.bsheet.save_edits()
        self.csvopt.select_layout('foobar') # no crash
        # the account doesn't exist, fallback to <New Account>
        eq_(self.csvopt.selected_target_index, 0)
    
    def test_select_same_layout_doesnt_refresh_gui(self):
        # Selecting the layout that's already selected doesn't trigger gui refreshes
        self.csvopt.select_layout('foobaz')
        self.check_gui_calls_partial(self.csvopt_gui, not_expected=['refresh_layout_menu'])
    

class FortisWithLoadedLayouts(TestCase):
    def setUp(self):
        self.app_gui = ApplicationGUI()
        self.app = Application(self.app_gui)
        self.document_gui = DocumentGUI()
        self.document = Document(self.document_gui, self.app)
        # None values can't be in the preferences. They have to be replaced by empty strings.
        default = {
            'name': 'foobar',
            'columns': [CsvField.Reference, CsvField.Date, '', CsvField.Amount, '', CsvField.Description],
            'excluded_lines': [0],
            'target_account': 'one',
        }
        foobar = {
            'name': 'foobaz',
            'columns': [CsvField.Reference, CsvField.Date, '', CsvField.Amount, '', CsvField.Payee],
            'excluded_lines': [0]
        }
        self.app_gui.set_default(LAYOUT_PREFERENCE_NAME, [default, foobar])
        self.create_instances()
        self.add_accounts('one', 'two', 'three')
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
    
    def test_layouts(self):
        # The layouts have been correctly loaded
        eq_(self.csvopt.layout_names, ['Default', 'foobar', 'foobaz'])
        self.csvopt.select_layout('foobar')
        eq_(self.csvopt.columns[5], CsvField.Description)
        assert self.csvopt.line_is_excluded(0)
        eq_(self.csvopt.selected_target_index, 1)
        self.csvopt.select_layout('foobaz')
        eq_(self.csvopt.columns[5], CsvField.Payee)
        eq_(self.csvopt.columns[6], None) # columns for *all* layout have been adjusted
    

class DateFieldWithGarbage(TestCase):
    # The date field in date_field_with_garbage.csv has a date value with non-date data around the date
    def setUp(self):
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/date_field_with_garbage.csv'))
        self.csvopt.set_column_field(0, CsvField.Date)
        self.csvopt.set_column_field(2, CsvField.Description)
        self.csvopt.set_column_field(3, CsvField.Amount)
    
    def test_continue_import(self):
        # the date with garbage is correctly parsed
        self.csvopt.continue_import()
        eq_(len(self.itable), 2)
        eq_(self.itable[0].date_import, '14/01/2009')
    

class FortisThreeEmptyAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_accounts('one', 'two', 'three')
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
    
    def test_remember_selected_target_in_layout(self):
        self.csvopt.selected_target_index = 2
        self.csvopt.new_layout('foobar')
        self.csvopt.selected_target_index = 1
        self.csvopt.select_layout(None) # default
        eq_(self.csvopt.selected_target_index, 2)
    
    def test_target_account_names(self):
        eq_(self.csvopt.target_account_names, ['< New Account >', 'one', 'three', 'two'])
    

class FortisImportedThreeEmptyAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_accounts('one', 'two', 'three')
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        self.csvopt.set_line_excluded(0, True)
        self.csvopt.set_column_field(0, CsvField.Reference)
        self.csvopt.set_column_field(1, CsvField.Date)
        self.csvopt.set_column_field(3, CsvField.Amount)
        self.csvopt.set_column_field(5, CsvField.Description)
    
    def test_select_target_then_continue(self):
        # the selected target account is carried in the iwin
        self.csvopt.selected_target_index = 2 # three
        self.csvopt.continue_import()
        eq_(self.iwin.selected_target_account_index, 2)
    

class ImportFortisThenAnotherWithLessColumns(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        self.csvopt.new_layout('fortis')
        self.csvopt.set_column_field(6, CsvField.Transfer) # out of range of the other
        self.document.parse_file_for_import(self.filepath('csv/increase_decrease.csv')) # less columns (3)
    
    def test_access_last_column(self):
        # the columns are supposed to have been *reduced* so the gui doesn't try to access data that
        # doesn't exist
        try:
            self.csvopt.lines[0][len(self.csvopt.columns) - 1]
        except IndexError:
            self.fail("The number of columns should not be higher than what the lines contain")
    
    def test_select_fortis_layout_then_reload(self):
        # simply accessing a layout while having a csv with few columns loaded should not remove
        # columns from that layout
        self.csvopt.select_layout('fortis')
        self.document.parse_file_for_import(self.filepath('csv/fortis.csv'))
        self.csvopt.select_layout('fortis')
        eq_(self.csvopt.columns[6], CsvField.Transfer)
    
    def test_set_date_and_amount_then_import(self):
        # The csv loading process must not crash either, even if out-of-range columns are fed to it.
        self.csvopt.select_layout('fortis')
        self.csvopt.set_column_field(0, CsvField.Date)
        self.csvopt.set_column_field(1, CsvField.Increase)
        self.csvopt.set_column_field(2, CsvField.Decrease)
        self.csvopt.continue_import() # no crash
        eq_(len(self.itable), 3)
    

class IncreaseDecrease(TestCase):
    def setUp(self):
        # This file has two columns for amounts: increase and decrease. To make the matter worse,
        # it has a negative value in the decrease column, which must be ignored
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/increase_decrease.csv'))
        self.csvopt.set_column_field(0, CsvField.Date)
        self.csvopt.set_column_field(1, CsvField.Increase)
        self.csvopt.set_column_field(2, CsvField.Decrease)
        self.csvopt.set_line_excluded(0, True)
    
    def test_continue_import(self):
        self.csvopt.continue_import()
        eq_(len(self.itable), 3)
        eq_(self.itable[0].amount_import, '10.00')
        eq_(self.itable[1].amount_import, '-10.00')
        eq_(self.itable[2].amount_import, '-10.00')
    

class WeirdSep(TestCase):
    def setUp(self):
        # This file has mixed up field separators (, and ;). The sniffer will auto-detect the comma
        # as a field sep, but through the csv options panel, it should be possible to specify
        # another field sep.
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/weird_sep.csv'))
    
    def test_field_separator(self):
        # the field_separator member contains the currently used field sep.
        eq_(self.csvopt.field_separator, ',')
    
    def test_rescan(self):
        # It's possible to specify a new field sep and then rescan the csv.
        # unicode separator is used because we must test that ew automatically encode the delimiter.
        # (csv.Reader only accepts strings instances)
        self.csvopt.field_separator = u';'
        self.csvopt.rescan()
        eq_(self.csvopt.lines[0], ['foo,bar', 'foo,baz'])
    
    def test_set_long_separator(self):
        # csv dialect requires a char of 1 in length. If the input is bigger, just use the first char
        self.csvopt.field_separator = u';foo'
        self.csvopt.rescan()
        eq_(self.csvopt.lines[0], ['foo,bar', 'foo,baz'])
    
    def test_set_non_latin_separator(self):
        # a csv dialect requires a string delimiter, not a unicode one. encode unicode automatically,
        # an abort on errors.
        self.csvopt.field_separator = u'ł'
        self.csvopt.rescan() # no crash
    
    def test_set_null_separator(self):
        # ignore attemps to set an empty separator
        self.csvopt.field_separator = ''
        self.csvopt.rescan() # no crash
    

class AmountWithDollarSign(TestCase):
    def setUp(self):
        # This file has a $ sign in its amount values.
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/amount_with_dollar_sign.csv'))
        self.csvopt.set_column_field(0, CsvField.Date)
        self.csvopt.set_column_field(1, CsvField.Amount)
    
    def test_import(self):
        # No crash and the correct amounts are parsed
        self.csvopt.continue_import() # no crash
        eq_(self.itable[0].amount_import, '10.00')
        eq_(self.itable[1].amount_import, '42.00')
    

class ShortDates(TestCase):
    def setUp(self):
        # This file has very short dates in m/d/y format
        self.create_instances()
        self.document.parse_file_for_import(self.filepath('csv/short_dates.csv'))
        self.csvopt.set_column_field(0, CsvField.Date)
        self.csvopt.set_column_field(1, CsvField.Amount)
    
    def test_import(self):
        # No crash and the correct amounts are parsed
        self.csvopt.continue_import() # no crash
        eq_(self.itable[0].date_import, '04/01/2010')
        eq_(self.itable[1].date_import, '29/01/2010')
    
