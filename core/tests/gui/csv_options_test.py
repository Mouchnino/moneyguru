# Created By: Virgil Dupras
# Created On: 2009-01-18
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_

from ..base import ApplicationGUI, TestApp, with_app, testdata
from ...app import Application
from ...gui.csv_options import LAYOUT_PREFERENCE_NAME
from ...loader.csv import CsvField

#---
def test_invalid_default():
    app_gui = ApplicationGUI()
    app_gui.defaults[LAYOUT_PREFERENCE_NAME] = 'invalid'
    TestApp(app=Application(app_gui)) # no crash when CSVOptions is created

#---
@with_app(TestApp)
def test_dont_crash_on_invalid_utf8_characters(app):
    app.doc.parse_file_for_import(testdata.filepath('csv/invalid_utf8_char.csv'))
    app.csvopt.encoding_index = 1
    app.csvopt.rescan() # no crash
    eq_(app.csvopt.lines[0][1], 'description')
    eq_(app.csvopt.lines[0][2], 'payee')

#---
def app_import_fortis():
    app = TestApp()
    app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
    expected_calls = ['refresh_layout_menu', 'refresh_columns', 'refresh_lines',
        'refresh_targets', 'show']
    app.csvopt_gui.check_gui_calls(expected_calls)
    return app

@with_app(app_import_fortis)
def test_fortis_columns(app):
    eq_(app.csvopt.columns, [None] * 8)

@with_app(app_import_fortis)
def test_continue_import_without_columns(app):
    # because the columns haven't been set, the iwin is not supposed to be brought and an error
    # message is supposed to pop.
    app.csvopt.continue_import()
    app.iwin_gui.check_gui_calls_partial(not_expected=['show'])
    app.csvopt_gui.check_gui_calls(['show_message'])

@with_app(app_import_fortis)
def test_delete_selected_layout_do_nothing_on_default(app):
    # There used to be an assert in delete_selected_layout to make sure the default layout was
    # never deleted, but on PyQt, there doesn't seem to be an easy way to disable a menu item
    # in a combobox, so we'll just make delete_selected_layout do nothing.
    app.csvopt.delete_selected_layout() # do nothing, no assertion error
    eq_(app.csvopt.layout_names, ['Default'])

@with_app(app_import_fortis)
def test_fortis_exclude_first_line(app):
    app.csvopt.set_line_excluded(0, True)
    assert app.csvopt.line_is_excluded(0)

@with_app(app_import_fortis)
def test_fortis_get_column_name(app):
    eq_(app.csvopt.get_column_name(3), 'None')

@with_app(app_import_fortis)
def test_fortis_lines(app):
    eq_(len(app.csvopt.lines), 19)

@with_app(app_import_fortis)
def test_set_column_field(app):
    app.csvopt.set_column_field(1, CsvField.Date)
    eq_(app.csvopt.get_column_name(1), 'Date')
    app.csvopt_gui.check_gui_calls(['refresh_columns_name'])

#---
def app_import_fortis_with_wrong_date_col():
    app = TestApp()
    app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
    app.csvopt.set_column_field(5, CsvField.Date) #description
    app.csvopt.set_column_field(3, CsvField.Amount)
    app.clear_gui_calls()
    return app

@with_app(app_import_fortis_with_wrong_date_col)
def test_dont_change_line_values_on_contrinue_import(app):
    # Continuing the import hasn't change the values of the lines.
    previous_value = app.csvopt.lines[2][5]
    app.csvopt.continue_import()
    eq_(app.csvopt.lines[2][5], previous_value)

@with_app(app_import_fortis_with_wrong_date_col)
def test_show_error_message_on_wrong_date_col(app):
    # if the field date is set to a non-date column, raise an appropriate error (with show_message)
    app.csvopt.continue_import()
    app.csvopt_gui.check_gui_calls(['show_message'])

#---
def app_import_fortis_exclude_first_line_and_set_fields():
    app = TestApp()
    app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
    app.csvopt.set_line_excluded(0, True)
    app.csvopt.set_column_field(0, CsvField.Reference)
    app.csvopt.set_column_field(1, CsvField.Date)
    app.csvopt.set_column_field(3, CsvField.Amount)
    app.csvopt.set_column_field(5, CsvField.Description)
    app.clear_gui_calls()
    return app

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_continue_import_with_fields_set(app):
    # sets the columns in app.doc.loader and continues importing
    app.csvopt.continue_import()
    app.csvopt_gui.check_gui_calls(['hide'])
    app.iwin_gui.check_gui_calls(['refresh_tabs', 'refresh_target_accounts', 'show'])
    eq_(len(app.iwin.panes), 1)
    eq_(app.iwin.panes[0].name, 'CSV Import')
    eq_(app.iwin.panes[0].count, 18)
    eq_(len(app.itable), 18)
    eq_(app.itable[0].date_import, '01/12/2008')
    eq_(app.itable[0].description_import, 'RETRAIT A UN DISTRIBUTEUR FORTIS')
    eq_(app.itable[0].amount_import, '-100.00')

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_continue_import_without_the_first_line_being_excluded(app):
    # When the user forgets to exclude a header line, just ignore that line in guess_date_format()
    app.csvopt.set_line_excluded(0, False)
    app.csvopt.continue_import()
    eq_(len(app.itable), 18)
    eq_(app.itable[0].date_import, '01/12/2008')

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_create_and_navigate_layouts(app):
    app.csvopt.new_layout('foobar') # 'foobar' is selected
    app.csvopt_gui.check_gui_calls(['refresh_layout_menu'])
    eq_(app.csvopt.layout_names, ['Default', 'foobar'])
    app.csvopt.set_column_field(5, CsvField.Payee)
    app.clear_gui_calls()
    app.csvopt.select_layout(None) # default
    app.csvopt_gui.check_gui_calls(['refresh_columns_name', 'refresh_lines', 'refresh_targets'])
    eq_(app.csvopt.columns[5], CsvField.Description)
    app.csvopt.select_layout('foobar')
    eq_(app.csvopt.columns[5], CsvField.Payee)

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_new_layout_with_empty_name(app):
    # when trying to add a layout with an empty name, do nothing
    app.csvopt.new_layout('')
    app.csvopt.new_layout(None)
    eq_(len(app.csvopt.layout_names), 1)

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_rename_layout_with_empty_name(app):
    # when trying to add a layout with an empty name, do nothing
    app.csvopt.rename_selected_layout('')
    app.csvopt.rename_selected_layout(None)
    eq_(app.csvopt.layout.name, 'Default')

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_set_same_field_on_another_column(app):
    # if a field is already set somewhere and that another column sets the same field elsewhere,
    # clear the other column
    app.csvopt.set_column_field(2, CsvField.Date)
    eq_(app.csvopt.get_column_name(1), 'None')

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_set_wrong_amount_column_and_continue_import(app):
    # When setting the amount column on a wrong column, don't continue import and show an error
    # message.
    app.csvopt.set_column_field(5, CsvField.Amount)
    app.clear_gui_calls()
    app.csvopt.continue_import()
    app.csvopt_gui.check_gui_calls(['show_message'])

@with_app(app_import_fortis_exclude_first_line_and_set_fields)
def test_set_wrong_increase_decrease_column_and_continue_import(app):
    # When setting the amount column on a wrong column, don't continue import and show an error
    # message.
    app.csvopt.set_column_field(3, CsvField.Increase)
    app.csvopt.set_column_field(4, CsvField.Decrease)
    app.clear_gui_calls()
    app.csvopt.continue_import()
    app.csvopt_gui.check_gui_calls(['show_message'])

#---
def app_lots_of_noise():
    app = TestApp()
    app.doc.parse_file_for_import(testdata.filepath('csv/lots_of_noise.csv'))
    return app

@with_app(app_lots_of_noise)
def test_use_latin1_encoding_initially(app):
    # This file contains umlauts encoded in latin-1. Make sure they are correctly decoded
    s = app.csvopt.lines[0][0]
    assert isinstance(s, str)
    assert 'ä' in s

#---
def app_lots_of_noise_ready_to_import():
    app = TestApp()
    app.doc.parse_file_for_import(testdata.filepath('csv/lots_of_noise.csv'))
    app.csvopt.set_line_excluded(0, True)
    app.csvopt.set_line_excluded(1, True)
    app.csvopt.set_line_excluded(2, True)
    app.csvopt.set_line_excluded(3, True)
    app.csvopt.set_line_excluded(4, True)
    app.csvopt.set_line_excluded(7, True)
    app.csvopt.set_column_field(0, CsvField.Date)
    app.csvopt.set_column_field(2, CsvField.Description)
    app.csvopt.set_column_field(3, CsvField.Amount)
    return app

@with_app(app_lots_of_noise_ready_to_import)
def test_continue_import_of_lots_of_noise(app):
    app.csvopt.continue_import()
    eq_(len(app.itable), 2)
    eq_(app.itable[0].date_import, '14/01/2009')
    eq_(app.itable[0].description_import, '1234512345123451 AMAZON.SER VICES S. 090114P3TX4612XG AMAZON.SERVICES S.A.R.L - E U-DE DR. THOMAS ECKHOLD')
    eq_(app.itable[0].amount_import, '-99.99')

@with_app(app_lots_of_noise_ready_to_import)
def test_load_fortis_after_lots_of_noise(app):
    # when loading another CSV, keep line exclusions that happen to be last *last*
    app.csvopt.set_line_excluded(6, True) # should also work for the line before the last
    app.csvopt.new_layout('fortis') # let's save it
    app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
    app.csvopt.select_layout('fortis')
    assert not app.csvopt.line_is_excluded(6)
    assert not app.csvopt.line_is_excluded(7)
    assert app.csvopt.line_is_excluded(17)
    assert app.csvopt.line_is_excluded(18)

@with_app(app_lots_of_noise_ready_to_import)
def test_reinclude_last_line(app):
    # it's possible to re-include the last line. Previously, due to the negative index scheme,
    # it wouldn't be possible.
    app.csvopt.set_line_excluded(7, False)
    assert not app.csvopt.line_is_excluded(7)

#---
def app_fortis_with_two_layouts():
    app = TestApp()
    app.add_accounts('one', 'two', 'three')
    app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
    app.csvopt.set_line_excluded(0, True)
    app.csvopt.set_column_field(0, CsvField.Reference)
    app.csvopt.set_column_field(1, CsvField.Date)
    app.csvopt.set_column_field(3, CsvField.Amount)
    app.csvopt.set_column_field(5, CsvField.Description)
    app.csvopt.new_layout('foobar') # 'foobar' is selected
    app.csvopt.selected_target_index = 1 # one
    app.csvopt.new_layout('foobaz') # 'foobaz' is selected
    app.csvopt.set_column_field(5, CsvField.Payee)
    app.clear_gui_calls()
    return app

@with_app(app_fortis_with_two_layouts)
def test_close_document_saves_prefs(app):
    # when the document is closed, layouts are saved to preferences
    app.doc.close()
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
    eq_(app.app_gui.get_default(LAYOUT_PREFERENCE_NAME), [default, foobar])

@with_app(app_fortis_with_two_layouts)
def test_delete_selected_layout(app):
    app.csvopt.delete_selected_layout()
    app.csvopt_gui.check_gui_calls(['refresh_layout_menu', 'refresh_columns_name', 'refresh_lines'])
    eq_(app.csvopt.layout_names, ['Default', 'foobar'])
    eq_(app.csvopt.layout.name, 'Default')

@with_app(app_fortis_with_two_layouts)
def test_load_another_import_selects_default_layout(app):
    # when a file is loaded, select the default layout, and reset it
    app.doc.parse_file_for_import(testdata.filepath('csv/lots_of_noise.csv'))
    eq_(app.csvopt.layout.name, 'Default')
    assert app.csvopt.columns[5] is None

@with_app(app_fortis_with_two_layouts)
def test_rename_selected_layout(app):
    app.csvopt.rename_selected_layout('foobaz')
    app.csvopt_gui.check_gui_calls(['refresh_layout_menu'])
    eq_(app.csvopt.layout_names, ['Default', 'foobar', 'foobaz'])

@with_app(app_fortis_with_two_layouts)
def test_rename_target_account_doesnt_crash_layouts(app):
    # When renaming an account targeted by a layout doesn't cause a crash next time this layout
    # is loaded.
    app.bsheet.selected = app.bsheet.assets[0] # 'one', the target account
    app.bsheet.assets[0].name = 'renamed'
    app.bsheet.save_edits()
    app.csvopt.select_layout('foobar') # no crash
    # the account doesn't exist, fallback to <New Account>
    eq_(app.csvopt.selected_target_index, 0)

@with_app(app_fortis_with_two_layouts)
def test_select_same_layout_doesnt_refresh_gui(app):
    # Selecting the layout that's already selected doesn't trigger gui refreshes
    app.csvopt.select_layout('foobaz')
    app.csvopt_gui.check_gui_calls_partial(not_expected=['refresh_layout_menu'])

#---
def app_fortis_with_loaded_layouts():
    app_gui = ApplicationGUI()
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
    app_gui.set_default(LAYOUT_PREFERENCE_NAME, [default, foobar])
    app = TestApp(app=Application(app_gui))
    app.add_accounts('one', 'two', 'three')
    app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
    return app

@with_app(app_fortis_with_loaded_layouts)
def test_layouts_correctly_load_from_prefs(app):
    # The layouts have been correctly loaded
    eq_(app.csvopt.layout_names, ['Default', 'foobar', 'foobaz'])
    app.csvopt.select_layout('foobar')
    eq_(app.csvopt.columns[5], CsvField.Description)
    assert app.csvopt.line_is_excluded(0)
    eq_(app.csvopt.selected_target_index, 1)
    app.csvopt.select_layout('foobaz')
    eq_(app.csvopt.columns[5], CsvField.Payee)
    eq_(app.csvopt.columns[6], None) # columns for *all* layout have been adjusted

#---
def app_date_field_with_garbage():
    # The date field in date_field_with_garbage.csv has a date value with non-date data around the date
    app = TestApp()
    app.doc.parse_file_for_import(testdata.filepath('csv/date_field_with_garbage.csv'))
    app.csvopt.set_column_field(0, CsvField.Date)
    app.csvopt.set_column_field(2, CsvField.Description)
    app.csvopt.set_column_field(3, CsvField.Amount)
    return app

@with_app(app_date_field_with_garbage)
def test_continue_import_parses_date_with_garbage_correctly(app):
    # the date with garbage is correctly parsed
    app.csvopt.continue_import()
    eq_(len(app.itable), 2)
    eq_(app.itable[0].date_import, '14/01/2009')

#---
def app_fortis_with_three_empty_accounts():
    app = TestApp()
    app.add_accounts('one', 'two', 'three')
    app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
    return app

@with_app(app_fortis_with_three_empty_accounts)
def test_remember_selected_target_in_layout(app):
    app.csvopt.selected_target_index = 2
    app.csvopt.new_layout('foobar')
    app.csvopt.selected_target_index = 1
    app.csvopt.select_layout(None) # default
    eq_(app.csvopt.selected_target_index, 2)

@with_app(app_fortis_with_three_empty_accounts)
def test_target_account_names(app):
    eq_(app.csvopt.target_account_names, ['< New Account >', 'one', 'three', 'two'])

@with_app(app_fortis_with_three_empty_accounts)
def test_set_fields_select_target_then_continue(app):
    # the selected target account is carried in the iwin
    app.csvopt.set_line_excluded(0, True)
    app.csvopt.set_column_field(0, CsvField.Reference)
    app.csvopt.set_column_field(1, CsvField.Date)
    app.csvopt.set_column_field(3, CsvField.Amount)
    app.csvopt.set_column_field(5, CsvField.Description)
    app.csvopt.selected_target_index = 2 # three
    app.csvopt.continue_import()
    eq_(app.iwin.selected_target_account_index, 2)

#---
class TestImportFortisThenAnotherWithLessColumns:
    def setup(self):
        app = TestApp()
        app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
        app.csvopt.new_layout('fortis')
        app.csvopt.set_column_field(6, CsvField.Transfer) # out of range of the other
        app.doc.parse_file_for_import(testdata.filepath('csv/increase_decrease.csv')) # less columns (3)
        return app
    
    @with_app(setup)
    def test_access_last_column(self, app):
        # the columns are supposed to have been *reduced* so the gui doesn't try to access data that
        # doesn't exist
        try:
            app.csvopt.lines[0][len(app.csvopt.columns) - 1]
        except IndexError:
            assert False, "The number of columns should not be higher than what the lines contain"
    
    @with_app(setup)
    def test_select_fortis_layout_then_reload(self, app):
        # simply accessing a layout while having a csv with few columns loaded should not remove
        # columns from that layout
        app.csvopt.select_layout('fortis')
        app.doc.parse_file_for_import(testdata.filepath('csv/fortis.csv'))
        app.csvopt.select_layout('fortis')
        eq_(app.csvopt.columns[6], CsvField.Transfer)
    
    @with_app(setup)
    def test_set_date_and_amount_then_import(self, app):
        # The csv loading process must not crash either, even if out-of-range columns are fed to it.
        app.csvopt.select_layout('fortis')
        app.csvopt.set_column_field(0, CsvField.Date)
        app.csvopt.set_column_field(1, CsvField.Increase)
        app.csvopt.set_column_field(2, CsvField.Decrease)
        app.csvopt.continue_import() # no crash
        eq_(len(app.itable), 3)
    

#---
class TestIncreaseDecrease:
    def setup(self):
        # This file has two columns for amounts: increase and decrease. To make the matter worse,
        # it has a negative value in the decrease column, which must be ignored
        app = TestApp()
        app.doc.parse_file_for_import(testdata.filepath('csv/increase_decrease.csv'))
        app.csvopt.set_column_field(0, CsvField.Date)
        app.csvopt.set_column_field(1, CsvField.Increase)
        app.csvopt.set_column_field(2, CsvField.Decrease)
        app.csvopt.set_line_excluded(0, True)
        return app
    
    @with_app(setup)
    def test_continue_import(self, app):
        app.csvopt.continue_import()
        eq_(len(app.itable), 3)
        eq_(app.itable[0].amount_import, '10.00')
        eq_(app.itable[1].amount_import, '-10.00')
        eq_(app.itable[2].amount_import, '-10.00')
    

#---
class TestWeirdSep:
    def setup(self):
        # This file has mixed up field separators (, and ;). The sniffer will auto-detect the comma
        # as a field sep, but through the csv options panel, it should be possible to specify
        # another field sep.
        app = TestApp()
        app.doc.parse_file_for_import(testdata.filepath('csv/weird_sep.csv'))
        return app
    
    @with_app(setup)
    def test_field_separator(self, app):
        # the field_separator member contains the currently used field sep.
        eq_(app.csvopt.field_separator, ',')
    
    @with_app(setup)
    def test_rescan(self, app):
        # It's possible to specify a new field sep and then rescan the csv.
        app.csvopt.field_separator = ';'
        app.csvopt.rescan()
        eq_(app.csvopt.lines[0], ['foo,bar', 'foo,baz'])
    
    @with_app(setup)
    def test_set_long_separator(self, app):
        # csv dialect requires a char of 1 in length. If the input is bigger, just use the first char
        app.csvopt.field_separator = ';foo'
        app.csvopt.rescan()
        eq_(app.csvopt.lines[0], ['foo,bar', 'foo,baz'])
    
    @with_app(setup)
    def test_set_non_latin_separator(self, app):
        # a csv dialect requires a string delimiter, not a unicode one. encode unicode automatically,
        # an abort on errors.
        app.csvopt.field_separator = 'ł'
        app.csvopt.rescan() # no crash
    
    @with_app(setup)
    def test_set_null_separator(self, app):
        # ignore attemps to set an empty separator
        app.csvopt.field_separator = ''
        app.csvopt.rescan() # no crash
    

#---
class TestAmountWithDollarSign:
    def setup(self):
        # This file has a $ sign in its amount values.
        app = TestApp()
        app.doc.parse_file_for_import(testdata.filepath('csv/amount_with_dollar_sign.csv'))
        app.csvopt.set_column_field(0, CsvField.Date)
        app.csvopt.set_column_field(1, CsvField.Amount)
        return app
    
    @with_app(setup)
    def test_import(self, app):
        # No crash and the correct amounts are parsed
        app.csvopt.continue_import() # no crash
        eq_(app.itable[0].amount_import, '10.00')
        eq_(app.itable[1].amount_import, '-42.00')
    

#---
class TestShortDates:
    def setup(self):
        # This file has very short dates in m/d/y format
        app = TestApp()
        app.doc.parse_file_for_import(testdata.filepath('csv/short_dates.csv'))
        app.csvopt.set_column_field(0, CsvField.Date)
        app.csvopt.set_column_field(1, CsvField.Amount)
        return app
    
    @with_app(setup)
    def test_import(self, app):
        # No crash and the correct amounts are parsed
        app.csvopt.continue_import() # no crash
        eq_(app.itable[0].date_import, '04/01/2010')
        eq_(app.itable[1].date_import, '29/01/2010')
    

#---
class TestUtf8Encoded:
    def setup(self):
        # This file has utf8-encoded non-ascii descriptions
        app = TestApp()
        app.doc.parse_file_for_import(testdata.filepath('csv/utf8_encoded.csv'))
        # At this point, the CSV file is parsed with latin-1 encoding, it's normal. The user is
        # supposed to select the utf-8 encoding and click Rescan.
        return app
    
    @with_app(setup)
    def test_rescan_with_utf8_encoding(self, app):
        # Selecting the utf-8 encoding and clicking rescan re-opens the file with the correct
        # encoding.
        app.csvopt.encoding_index = 1
        app.csvopt.rescan()
        eq_(app.csvopt.lines[1][1], 'fôø')
        eq_(app.csvopt.lines[2][1], 'bàr')
    
#---
def app_simple_csv():
    app = TestApp()
    app.doc.parse_file_for_import(testdata.filepath('csv/simple.csv'))
    app.csvopt.set_column_field(0, CsvField.Date)
    app.csvopt.set_column_field(1, CsvField.Description)
    app.csvopt.set_column_field(2, CsvField.Payee)
    app.csvopt.set_column_field(4, CsvField.Transfer)
    app.csvopt.set_column_field(5, CsvField.Amount)
    return app

@with_app(app_simple_csv)
def test_two_columns_with_description(app):
    # When two columns have a Description field, merge them together.
    app.csvopt.set_column_field(3, CsvField.Description)
    app.csvopt.continue_import()
    eq_(app.itable[0].description_import, 'description whatever')

@with_app(app_simple_csv)
def test_two_columns_with_payee(app):
    # When two columns have a Payee field, merge them together.
    app.csvopt.set_column_field(3, CsvField.Payee)
    app.csvopt.continue_import()
    eq_(app.itable[0].payee_import, 'payee whatever')