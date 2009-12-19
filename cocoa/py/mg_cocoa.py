# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# index_path are arrays of int. Convert them from NSIndexPath with cocoalib.Utils.indexPath2Array
import objc
from Foundation import *
from AppKit import *
import logging

import hsutil.cocoa
from hsutil.path import Path
from hsutil.currency import Currency, USD

from moneyguru.app import Application
from moneyguru.document import (Document, FILTER_UNASSIGNED, FILTER_INCOME, FILTER_EXPENSE, 
    FILTER_TRANSFER, FILTER_RECONCILED, FILTER_NOTRECONCILED)
from moneyguru.exception import FileFormatError
from moneyguru.gui.account_panel import AccountPanel
from moneyguru.gui.account_pie_chart import AssetsPieChart, LiabilitiesPieChart, IncomePieChart, ExpensesPieChart
from moneyguru.gui.account_reassign_panel import AccountReassignPanel
from moneyguru.gui.bar_graph import BarGraph
from moneyguru.gui.balance_graph import BalanceGraph
from moneyguru.gui.balance_sheet import BalanceSheet
from moneyguru.gui.budget_table import BudgetTable
from moneyguru.gui.budget_panel import BudgetPanel
from moneyguru.gui.csv_options import CSVOptions, FIELD_ORDER as CSV_FIELD_ORDER
from moneyguru.gui.custom_date_range_panel import CustomDateRangePanel
from moneyguru.gui.date_widget import DateWidget
from moneyguru.gui.entry_print import EntryPrint
from moneyguru.gui.entry_table import EntryTable
from moneyguru.gui.filter_bar import FilterBar, EntryFilterBar
from moneyguru.gui.income_statement import IncomeStatement
from moneyguru.gui.import_table import ImportTable
from moneyguru.gui.import_window import ImportWindow, DAY, MONTH, YEAR
from moneyguru.gui.main_window import MainWindow
from moneyguru.gui.mass_edition_panel import MassEditionPanel
from moneyguru.gui.net_worth_graph import NetWorthGraph
from moneyguru.gui.print_view import PrintView
from moneyguru.gui.profit_graph import ProfitGraph
from moneyguru.gui.schedule_panel import SchedulePanel
from moneyguru.gui.schedule_table import ScheduleTable
from moneyguru.gui.search_field import SearchField
from moneyguru.gui.split_table import SplitTable
from moneyguru.gui.transaction_panel import TransactionPanel
from moneyguru.gui.transaction_print import TransactionPrint
from moneyguru.gui.transaction_table import TransactionTable
from moneyguru.model.date import clean_format

# These imports below are a workaround for py2app, which doesn't like relative imports
import csv
from moneyguru import const
from moneyguru.gui import base, chart, graph, report, table, tree
from moneyguru.loader import base, csv, native, ofx, qif
from moneyguru.model import (account, amount, currency, date, oven, recurrence, transaction,
    transaction_list, completion, undo)

class PyMoneyGuruApp(NSObject):
    def initWithCocoa_(self, cocoa):
        self = NSObject.init(self)
        self.cocoa = cocoa
        LOGGING_LEVEL = logging.DEBUG if NSUserDefaults.standardUserDefaults().boolForKey_('debug') else logging.WARNING
        logging.basicConfig(level=LOGGING_LEVEL, format='%(levelname)s %(message)s')
        logging.debug('started in debug mode')
        hsutil.cocoa.install_exception_hook()
        std_caches_path = Path(NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, True)[0])
        cache_path = std_caches_path + 'moneyGuru'
        currency_code = NSLocale.currentLocale().objectForKey_(NSLocaleCurrencyCode)
        logging.info('Currency code: {0}'.format(currency_code))
        try:
            system_currency = Currency(currency_code)
        except ValueError: # currency does not exist
            logging.warning('System currency {0} is not supported. Falling back to USD.'.format(currency_code))
            system_currency = USD
        NSDateFormatter.setDefaultFormatterBehavior_(NSDateFormatterBehavior10_4)
        f = NSDateFormatter.alloc().init()
        f.setDateStyle_(NSDateFormatterShortStyle)
        f.setTimeStyle_(NSDateFormatterNoStyle)
        date_format = f.dateFormat()
        logging.info('System date format: %s' % date_format)
        date_format = clean_format(date_format)
        logging.info('Cleaned date format: %s' % date_format)
        NSNumberFormatter.setDefaultFormatterBehavior_(NSNumberFormatterBehavior10_4)
        f = NSNumberFormatter.alloc().init()
        decimal_sep = f.decimalSeparator()
        grouping_sep = f.groupingSeparator()
        logging.info('System numeric separators: %s and %s' % (grouping_sep, decimal_sep))
        self.py = Application(self, date_format=date_format, decimal_sep=decimal_sep, 
            grouping_sep=grouping_sep, default_currency=system_currency, cache_path=cache_path)
        return self
    
    def free(self): # see GUIProxy
        if hasattr(self, 'cocoa'):
            del self.cocoa
    
    def get_default(self, key_name):
        raw = NSUserDefaults.standardUserDefaults().objectForKey_(key_name)
        result = hsutil.cocoa.pythonify(raw)
        return result
    
    def set_default(self, key_name, value):
        NSUserDefaults.standardUserDefaults().setObject_forKey_(value, key_name)
    
    #--- Preferences
    @objc.signature('i@:')
    def firstWeekday(self):
        return self.py.first_weekday
    
    @objc.signature('v@:i')
    def setFirstWeekday_(self, weekday):
        self.py.first_weekday = weekday
    
    @objc.signature('i@:')
    def aheadMonths(self):
        return self.py.ahead_months
    
    @objc.signature('v@:i')
    def setAheadMonths_(self, months):
        self.py.ahead_months = months
    
    # The selector in the pref pane is 0-based, the py side's pref is 1-based
    @objc.signature('i@:')
    def yearStartMonth(self):
        return self.py.year_start_month - 1
    
    @objc.signature('v@:i')
    def setYearStartMonth_(self, month):
        self.py.year_start_month = month + 1
    
    @objc.signature('i@:')
    def autoSaveInterval(self):
        return self.py.autosave_interval
    
    @objc.signature('v@:i')
    def setAutoSaveInterval_(self, minutes):
        self.py.autosave_interval = minutes
    
    @objc.signature('i@:')
    def dontUnreconcile(self):
        return self.py.dont_unreconcile
    
    @objc.signature('v@:i')
    def setDontUnreconcile_(self, flag):
        self.py.dont_unreconcile = flag
    
    #---Registration
    @objc.signature('i@:')
    def isRegistered(self):
        return self.py.registered
    
    @objc.signature('i@:@@')
    def isCodeValid_withEmail_(self, code, email):
        return self.py.is_code_valid(code, email)
    
    def setRegisteredCode_andEmail_(self, code, email):
        self.py.set_registration(code, email)
    
    #--- Python -> Cocoa
    def setup_as_registered(self):
        self.cocoa.setupAsRegistered()
    

class PyDocument(NSObject):
    def initWithCocoa_pyParent_(self, cocoa, pyparent):
        self = NSObject.init(self)
        self.cocoa = cocoa
        self.py = Document(self, pyparent.py)
        self.py.connect()
        return self
    
    #--- Date range
    def selectPrevDateRange(self):
        self.py.select_prev_date_range()

    def selectMonthRange(self):
        self.py.select_month_range()

    def selectQuarterRange(self):
        self.py.select_quarter_range()

    def selectYearRange(self):
        self.py.select_year_range()
    
    def selectYearToDateRange(self):
        self.py.select_year_to_date_range()
    
    def selectNextDateRange(self):
        self.py.select_next_date_range()
    
    def selectTodayDateRange(self):
        self.py.select_today_date_range()
    
    def selectRunningYearRange(self):
        self.py.select_running_year_range()
    
    def selectCustomDateRange(self):
        self.py.select_custom_date_range()
    
    def dateRangeDisplay(self):
        return self.py.date_range.display
    
    #--- Reconciliation
    def toggleReconciliationMode(self):
        self.py.toggle_reconciliation_mode()

    @objc.signature('i@:')
    def inReconciliationMode(self):
        return self.py.in_reconciliation_mode()
    
    #--- Undo
    @objc.signature('i@:')
    def canUndo(self):
        return self.py.can_undo()
    
    def undoDescription(self):
        return self.py.undo_description()
    
    def undo(self):
        self.py.undo()
    
    @objc.signature('i@:')
    def canRedo(self):
        return self.py.can_redo()
    
    def redoDescription(self):
        return self.py.redo_description()
    
    def redo(self):
        self.py.redo()
    
    #--- Misc
    def adjustExampleFile(self):
        self.py.adjust_example_file()
    
    def loadFromFile_(self, filename):
        try:
            self.py.load_from_xml(filename)
        except FileFormatError as e:
            return unicode(e)
    
    def saveToFile_(self, filename):
        self.py.save_to_xml(filename)
    
    def saveToQIF_(self, filename):
        self.py.save_to_qif(filename)
    
    def import_(self, filename):
        try:
            self.py.parse_file_for_import(filename)
        except FileFormatError, e:
            return unicode(e)
    
    @objc.signature('i@:')
    def isDirty(self):
        return self.py.is_dirty()
    
    def stopEdition(self):
        self.py.stop_edition()
    
    @objc.signature('i@:')
    def transactionCount(self):
        return len(self.py.transactions)
    
    @objc.signature('i@:')
    def shownAccountIsBalanceSheet(self):
        return self.py.shown_account is not None and self.py.shown_account.is_balance_sheet_account()
    
    def close(self):
        self.py.close()
        self.py.disconnect()
    
    # temporary
    @objc.signature('i@:')
    def isRegistered(self):
        return self.py.app.registered
    
    def free(self): # see GUIProxy
        if hasattr(self, 'cocoa'):
            del self.cocoa
    
    #--- Python -> Cocoa
    def confirm_unreconciliation(self, affected_split_count):
        return self.cocoa.confirmUnreconciliation_(affected_split_count)
    
    def query_for_schedule_scope(self):
        return self.cocoa.queryForScheduleScope()
    

#--- Root classes

class GUIProxy(NSObject):
    def initWithCocoa_pyParent_(self, cocoa, pyparent):
        # In most cases, pyparent is a PyDocument
        self = NSObject.init(self)
        self.cocoa = cocoa
        self.py = self.py_class(self, pyparent.py)
        return self
    
    def free(self):
        # call this method only when you don't need to use this proxy anymore. you need to call this
        # if you want to release the cocoa side (self.cocoa is holding a refcount)
        # We don't delete py, it might be called after the free. It will be garbage collected anyway.
        # The if is because there is something happening giving a new ref to cocoa right after
        # the free, and then the ref gets to 1 again, free is called again.
        if hasattr(self, 'cocoa'):
            del self.cocoa
    
    #--- Python -> Cocoa
    def refresh(self):
        self.cocoa.refresh()
    
    def show_message(self, msg):
        self.cocoa.showMessage_(msg)

class PyListener(GUIProxy):
    def connect(self):
        self.py.connect()
    
    def disconnect(self):
        self.py.disconnect()
    
    def free(self):
        self.disconnect()
        GUIProxy.free(self)
    

class PyWindowController(PyListener):
    pass

# I know, it's ugly, but pyobjc doesn't work with multiple inheritance

class PyCompletion(PyListener):
    def completeValue_forAttribute_(self, value, column):
        return self.py.complete(value, column)
    
    def currentCompletion(self):
        return self.py.current_completion()
    
    def nextCompletion(self):
        return self.py.next_completion()
    
    def prevCompletion(self):
        return self.py.prev_completion()
    

class PyTable(PyCompletion):
    def add(self):
        self.py.add()
        
    def cancelEdits(self):
        self.py.cancel_edits()
    
    @objc.signature('i@:@i')
    def canEditColumn_atRow_(self, column, row):
        return self.py.can_edit_cell(column, row)
    
    def changeColumns_(self, columns):
        self.py.change_columns(list(columns))
    
    def deleteSelectedRows(self):
        self.py.delete()
    
    @objc.signature('i@:')
    def numberOfRows(self):
        return len(self.py)

    def saveEdits(self):
        self.py.save_edits()
    
    def selectRows_(self, rows):
        self.py.select(list(rows))

    def selectedRows(self):
        return self.py.selected_indexes
    
    @objc.signature('v@:@@i')
    def setValue_forColumn_row_(self, value, column, row):
        if column == 'from':
            column = 'from_'
        # this try except is important for the case while a row is in edition mode and the delete
        # button is clicked.
        try:
            setattr(self.py[row], column, value)
        except IndexError:
            logging.warning("Trying to set an out of bounds row ({0} / {1})".format(row, len(self.py)))
    
    @objc.signature('@@:@i')
    def valueForColumn_row_(self, column, row):
        if column == 'from':
            column = 'from_'
        try:
            return getattr(self.py[row], column)
        except IndexError:
            logging.warning("Trying to get an out of bounds row ({0} / {1})".format(row, len(self.py)))    
    
    #--- Python -> Cocoa
    def show_selected_row(self):
        self.cocoa.showSelectedRow()

    def start_editing(self):
        self.cocoa.startEditing()

    def stop_editing(self):
        self.cocoa.stopEditing()
    
    def update_selection(self):
        self.cocoa.updateSelection()
    

class PyTableWithDate(PyTable):
    @objc.signature('i@:')
    def isEditedRowInTheFuture(self):
        if self.py.edited is None:
            return False
        return self.py.edited.is_date_in_future()
    
    @objc.signature('i@:')
    def isEditedRowInThePast(self):
        if self.py.edited is None:
            return False
        return self.py.edited.is_date_in_past()
    

class PyChart(PyListener):
    def data(self):
        return self.py.data
    
    def title(self):
        return self.py.title
    
    def currency(self):
        return self.py.currency.code
    

class PyGraph(PyChart):
    @objc.signature('f@:')
    def xMin(self):
        return self.py.xmin

    @objc.signature('f@:')
    def xMax(self):
        return self.py.xmax
    
    @objc.signature('f@:')
    def yMin(self):
        return self.py.ymin
    
    @objc.signature('f@:')
    def yMax(self):
        return self.py.ymax
    
    @objc.signature('f@:')
    def xToday(self):
        return getattr(self.py, 'xtoday', 0) # bar charts don't have a xtoday attr
    
    def xLabels(self):
        return self.py.xlabels
    
    def xTickMarks(self):
        return self.py.xtickmarks
    
    def yLabels(self):
        return self.py.ylabels
    
    def yTickMarks(self):
        return self.py.ytickmarks
    

class PyOutline(PyListener):
    def cancelEdits(self):
        self.py.cancel_edits()
    
    @objc.signature('i@:@@')
    def canEditProperty_atPath_(self, property, path):
        node = self.py.get_node(path)
        assert node is self.py.selected
        return getattr(node, 'can_edit_' + property, False)
    
    def saveEdits(self):
        self.py.save_edits()
    
    def selectedPath(self):
        return self.py.get_path(self.py.selected)

    def setSelectedPath_(self, path):
        self.py.selected_path = path

    def property_valueAtPath_(self, property, path):
        try:
            return getattr(self.py.get_node(path), property)
        except IndexError:
            logging.warning(u"%r doesn't have a node at path %r", self.py, path)
            return u''
    
    def setProperty_value_atPath_(self, property, value, path):
        setattr(self.py.get_node(path), property, value)
    
    #--- Python -> Cocoa
    def start_editing(self):
        self.cocoa.startEditing()
    
    def stop_editing(self):
        self.cocoa.stopEditing()
    
    def update_selection(self):
        self.cocoa.updateSelection()
    

class PyReport(PyOutline):
    @objc.signature('i@:')
    def canDeleteSelected(self):
        return self.py.can_delete()
    
    def deleteSelected(self):
        self.py.delete()
    
    @objc.signature('i@:@@')
    def canMovePath_toPath_(self, source_path, dest_path):
        return self.py.can_move(source_path, dest_path)
    
    def movePath_toPath_(self, source_path, dest_path):
        self.py.move(source_path, dest_path)
    
    def showSelectedAccount(self):
        self.py.show_selected_account()
    
    @objc.signature('i@:')
    def canShowSelectedAccount(self):
        return self.py.can_show_selected_account
    
    def toggleExcluded(self):
        self.py.toggle_excluded()
    
    def expandPath_(self, path):
        self.py.expand_node(self.py.get_node(path))
        
    def collapsePath_(self, path):
        self.py.collapse_node(self.py.get_node(path))
    

class PyPanel(PyCompletion):
    def savePanel(self):
        self.py.save()
    
    # Python --> Cocoa
    def pre_load(self):
        self.cocoa.preLoad()
    
    def post_load(self):
        self.cocoa.postLoad()
    
    def pre_save(self):
        self.cocoa.preSave()
    

#--- GUI layer classes

class PyBalanceSheet(PyReport):
    py_class = BalanceSheet

class PyIncomeStatement(PyReport):
    py_class = IncomeStatement

class PyEntryTable(PyTableWithDate):
    py_class = EntryTable

    @objc.signature('i@:@i')
    def canMoveRows_to_(self, rows, position):
        return self.py.can_move(list(rows), position)

    @objc.signature('i@:i')
    def canReconcileEntryAtRow_(self, row):
        return self.py[row].can_reconcile()
    
    @objc.signature('i@:i')
    def isBalanceNegativeAtRow_(self, row):
        return self.py[row].is_balance_negative()
    
    @objc.signature('v@:@i')
    def moveRows_to_(self, rows, position):
        self.py.move(list(rows), position)

    @objc.signature('i@:')
    def shouldShowBalanceColumn(self):
        return self.py.should_show_balance_column()
    
    def toggleReconciled(self):
        self.py.toggle_reconciled()
    
    @objc.signature('v@:i')
    def toggleReconciledAtRow_(self, row_index):
        self.py[row_index].toggle_reconciled()
    
    def totals(self):
        return self.py.totals
    

class PyTransactionTable(PyTableWithDate):
    py_class = TransactionTable

    @objc.signature('i@:@i')
    def canMoveRows_to_(self, rows, position):
        return self.py.can_move(list(rows), position)
    
    @objc.signature('v@:@i')
    def moveRows_to_(self, rows, position):
        self.py.move(list(rows), position)

    def totals(self):
        return self.py.totals
    

class PyScheduleTable(PyTable):
    py_class = ScheduleTable
    
    def editItem(self):
        self.py.edit()
    

class PyBudgetTable(PyTable):
    py_class = BudgetTable
    
    def editItem(self):
        self.py.edit()
    

class PySearchField(PyListener):
    py_class = SearchField
    
    def query(self):
        return self.py.query
    
    def setQuery_(self, query):
        self.py.query = query
    

class PyFilterBar(PyListener):
    py_class = FilterBar
    
    def filterType(self):
        result = 'all'
        if self.py.filter_type is FILTER_UNASSIGNED:
            result = 'unassigned'
        elif self.py.filter_type is FILTER_INCOME:
            result = 'income'
        elif self.py.filter_type is FILTER_EXPENSE:
            result = 'expense'
        elif self.py.filter_type is FILTER_TRANSFER:
            result = 'transfer'
        elif self.py.filter_type is FILTER_RECONCILED:
            result = 'reconciled'
        elif self.py.filter_type is FILTER_NOTRECONCILED:
            result = 'not_reconciled'
        return result
    
    def setFilterType_(self, filter_type):
        value = None
        if filter_type == 'unassigned':
            value = FILTER_UNASSIGNED
        elif filter_type == 'income':
            value = FILTER_INCOME
        elif filter_type == 'expense':
            value = FILTER_EXPENSE
        elif filter_type == 'transfer':
            value = FILTER_TRANSFER
        elif filter_type == 'reconciled':
            value = FILTER_RECONCILED
        elif filter_type == 'not_reconciled':
            value = FILTER_NOTRECONCILED
        self.py.filter_type = value
    

class PyEntryFilterBar(PyFilterBar):
    py_class = EntryFilterBar
    
    #--- Python --> Cocoa    
    def disable_transfers(self):
        self.cocoa.disableTransfers()
    
    def enable_transfers(self):
        self.cocoa.enableTransfers()
    

class PyAccountPanel(PyPanel):
    py_class = AccountPanel
    
    def name(self):
        return self.py.name
    
    def setName_(self, name):
        self.py.name = name
    
    @objc.signature('i@:')
    def typeIndex(self):
        return self.py.type_index
    
    @objc.signature('@@:i')
    def setTypeIndex_(self, index):
        self.py.type_index = index
    
    @objc.signature('i@:')
    def currencyIndex(self):
        return self.py.currency_index
    
    @objc.signature('@@:i')
    def setCurrencyIndex_(self, index):
        self.py.currency_index = index
    
    def availableCurrencies(self):
        return ['%s - %s' % (currency.code, currency.name) for currency in Currency.all]
    

class PySplitTable(PyTable):
    py_class = SplitTable
    # pyparent is a PyTransactionPanel

class PyTransactionPanel(PyPanel):
    py_class = TransactionPanel

    def mctBalance(self):
        self.py.mct_balance()
    
    @objc.signature('i@:')
    def canDoMCTBalance(self):
        return self.py.can_do_mct_balance
    
    def date(self):
        return self.py.date
    
    def setDate_(self, value):
        self.py.date = value
    
    def description(self):
        return self.py.description
    
    def setDescription_(self, value):
        self.py.description = value
    
    def payee(self):
        return self.py.payee
    
    def setPayee_(self, value):
        self.py.payee = value
    
    def checkno(self):
        return self.py.checkno
    
    def setCheckno_(self, value):
        self.py.checkno = value
    
    #--- Python -> Cocoa
    def refresh_mct_button(self):
        self.cocoa.refreshMCTButton()
    

class PyMassEditionPanel(PyPanel):
    py_class = MassEditionPanel

    def availableCurrencies(self):
        return ['%s - %s' % (currency.code, currency.name) for currency in Currency.all]
    
    @objc.signature('i@:')
    def canChangeAccountsAndAmount(self):
        return self.py.can_change_accounts_and_amount
    
    @objc.signature('i@:')
    def dateEnabled(self):
        return self.py.date_enabled
    
    @objc.signature('v@:i')
    def setDateEnabled_(self, value):
        self.py.date_enabled = value
    
    @objc.signature('i@:')
    def descriptionEnabled(self):
        return self.py.description_enabled
    
    @objc.signature('v@:i')
    def setDescriptionEnabled_(self, value):
        self.py.description_enabled = value
    
    @objc.signature('i@:')
    def payeeEnabled(self):
        return self.py.payee_enabled
    
    @objc.signature('v@:i')
    def setPayeeEnabled_(self, value):
        self.py.payee_enabled = value
    
    @objc.signature('i@:')
    def checknoEnabled(self):
        return self.py.checkno_enabled
    
    @objc.signature('v@:i')
    def setChecknoEnabled_(self, value):
        self.py.checkno_enabled = value
    
    @objc.signature('i@:')
    def fromEnabled(self):
        return self.py.from_enabled
    
    @objc.signature('v@:i')
    def setFromEnabled_(self, value):
        self.py.from_enabled = value
    
    @objc.signature('i@:')
    def toEnabled(self):
        return self.py.to_enabled
    
    @objc.signature('v@:i')
    def setToEnabled_(self, value):
        self.py.to_enabled = value
    
    @objc.signature('i@:')
    def amountEnabled(self):
        return self.py.amount_enabled
    
    @objc.signature('v@:i')
    def setAmountEnabled_(self, value):
        self.py.amount_enabled = value
    
    @objc.signature('i@:')
    def currencyEnabled(self):
        return self.py.currency_enabled
    
    @objc.signature('v@:i')
    def setCurrencyEnabled_(self, value):
        self.py.currency_enabled = value
    
    def date(self):
        return self.py.date
    
    @objc.signature('v@:@')
    def setDate_(self, value):
        self.py.date = value
    
    def description(self):
        return self.py.description
    
    @objc.signature('v@:@')
    def setDescription_(self, value):
        self.py.description = value
    
    def payee(self):
        return self.py.payee
    
    @objc.signature('v@:@')
    def setPayee_(self, value):
        self.py.payee = value
    
    def checkno(self):
        return self.py.checkno
    
    @objc.signature('v@:@')
    def setCheckno_(self, value):
        self.py.checkno = value
    
    def fromAccount(self): # We cannot use the underscore to escape the kw. It messes with pyobjc
        return self.py.from_
    
    @objc.signature('v@:@')
    def setFromAccount_(self, value):
        self.py.from_ = value
    
    def to(self):
        return self.py.to
    
    @objc.signature('v@:@')
    def setTo_(self, value):
        self.py.to = value
    
    def amount(self):
        return self.py.amount
    
    @objc.signature('v@:@')
    def setAmount_(self, value):
        self.py.amount = value
    
    @objc.signature('i@:')
    def currencyIndex(self):
        return self.py.currency_index
    
    @objc.signature('v@:i')
    def setCurrencyIndex_(self, value):
        self.py.currency_index = value
    

class PySchedulePanel(PyPanel):
    py_class = SchedulePanel
    
    def startDate(self):
        return self.py.start_date
    
    def setStartDate_(self, value):
        self.py.start_date = value
    
    def stopDate(self):
        return self.py.stop_date
    
    def setStopDate_(self, value):
        self.py.stop_date = value
    
    def description(self):
        return self.py.description
    
    def setDescription_(self, value):
        self.py.description = value
    
    def payee(self):
        return self.py.payee
    
    def setPayee_(self, value):
        self.py.payee = value
    
    def checkno(self):
        return self.py.checkno
    
    def setCheckno_(self, value):
        self.py.checkno = value
    
    @objc.signature('i@:')
    def repeatEvery(self):
        return self.py.repeat_every
    
    @objc.signature('v@:i')
    def setRepeatEvery_(self, value):
        self.py.repeat_every = value
    
    def repeatEveryDesc(self):
        return self.py.repeat_every_desc
    
    @objc.signature('i@:')
    def repeatTypeIndex(self):
        return self.py.repeat_type_index
    
    @objc.signature('v@:i')
    def setRepeatTypeIndex_(self, value):
        self.py.repeat_type_index = value
    
    def repeatOptions(self):
        return self.py.repeat_options
    
    #--- Python -> Cocoa
    def refresh_repeat_every(self):
        self.cocoa.refreshRepeatEvery()
    
    def refresh_repeat_options(self):
        self.cocoa.refreshRepeatOptions()
    

class PyBudgetPanel(PyPanel):
    py_class = BudgetPanel
    
    def startDate(self):
        return self.py.start_date
    
    def setStartDate_(self, value):
        self.py.start_date = value
    
    def stopDate(self):
        return self.py.stop_date
    
    def setStopDate_(self, value):
        self.py.stop_date = value
    
    @objc.signature('i@:')
    def repeatEvery(self):
        return self.py.repeat_every
    
    @objc.signature('v@:i')
    def setRepeatEvery_(self, value):
        self.py.repeat_every = value
    
    def repeatEveryDesc(self):
        return self.py.repeat_every_desc
    
    @objc.signature('i@:')
    def repeatTypeIndex(self):
        return self.py.repeat_type_index
    
    @objc.signature('v@:i')
    def setRepeatTypeIndex_(self, value):
        self.py.repeat_type_index = value
    
    @objc.signature('i@:')
    def accountIndex(self):
        return self.py.account_index
    
    @objc.signature('v@:i')
    def setAccountIndex_(self, value):
        self.py.account_index = value
    
    @objc.signature('i@:')
    def targetIndex(self):
        return self.py.target_index
    
    @objc.signature('v@:i')
    def setTargetIndex_(self, value):
        self.py.target_index = value
    
    def amount(self):
        return self.py.amount
    
    def setAmount_(self, value):
        self.py.amount = value
    
    #--- Lists
    def repeatOptions(self):
        return self.py.repeat_options
    
    def accountOptions(self):
        return self.py.account_options
    
    def targetOptions(self):
        return self.py.target_options
    
    #--- Python -> Cocoa
    def refresh_repeat_every(self):
        self.cocoa.refreshRepeatEvery()
    
    def refresh_repeat_options(self):
        self.cocoa.refreshRepeatOptions()
    

class PyCustomDateRangePanel(PyListener):
    py_class = CustomDateRangePanel
    
    def loadPanel(self):
        self.py.load()
    
    def ok(self):
        self.py.ok()
    
    def startDate(self):
        return self.py.start_date
    
    def setStartDate_(self, value):
        self.py.start_date = value
    
    def endDate(self):
        return self.py.end_date
    
    def setEndDate_(self, value):
        self.py.end_date = value
    

class PyAccountReassignPanel(PyListener):
    py_class = AccountReassignPanel
    
    def loadPanel(self):
        self.py.load()
    
    def ok(self):
        self.py.ok()
    
    def availableAccounts(self):
        return self.py.available_accounts
    
    @objc.signature('i@:')
    def accountIndex(self):
        return self.py.account_index
    
    @objc.signature('v@:i')
    def setAccountIndex_(self, value):
        self.py.account_index = value
    

class PyBalanceGraph(PyGraph):
    py_class = BalanceGraph

class PyNetWorthGraph(PyGraph):
    py_class = NetWorthGraph

class PyBarGraph(PyGraph):
    py_class = BarGraph

class PyProfitGraph(PyGraph):
    py_class = ProfitGraph

class PyAssetsPieChart(PyChart):
    py_class = AssetsPieChart

class PyLiabilitiesPieChart(PyChart):
    py_class = LiabilitiesPieChart

class PyIncomePieChart(PyChart):
    py_class = IncomePieChart

class PyExpensesPieChart(PyChart):
    py_class = ExpensesPieChart

class PyMainWindow(PyListener):
    def initWithCocoa_pyParent_children_(self, cocoa, pyparent, children):
        self = NSObject.init(self)
        self.cocoa = cocoa
        pychildren = [child.py for child in children]
        self.py = MainWindow(self, pyparent.py, pychildren)
        return self
    
    def selectBalanceSheet(self):
        self.py.select_balance_sheet()
    
    def selectIncomeStatement(self):
        self.py.select_income_statement()
    
    def selectTransactionTable(self):
        self.py.select_transaction_table()
    
    def selectEntryTable(self):
        self.py.select_entry_table()
    
    @objc.signature('i@:')
    def canSelectEntryTable(self):
        return self.py.document.shown_account is not None
    
    def selectScheduleTable(self):
        self.py.select_schedule_table()
    
    def selectBudgetTable(self):
        self.py.select_budget_table()
    
    def selectNextView(self):
        self.py.select_next_view()
    
    def selectPreviousView(self):
        self.py.select_previous_view()
    
    @objc.signature('i@:')
    def canNavigateDateRange(self):
        return self.py.document.date_range.can_navigate
    
    def navigateBack(self):
        self.py.navigate_back()
    
    #--- Item Management
    def deleteItem(self):
        self.py.delete_item()
    
    def editItem(self):
        self.py.edit_item()
    
    def makeScheduleFromSelected(self):
        self.py.make_schedule_from_selected()
    
    def moveDown(self):
        self.py.move_down()
    
    def moveUp(self):
        self.py.move_up()
    
    def newItem(self):
        self.py.new_item()
    
    def newGroup(self):
        self.py.new_group()
    
    #--- Python -> Cocoa
    def animate_date_range_backward(self):
        self.cocoa.animateDateRangeBackward()
    
    def animate_date_range_forward(self):
        self.cocoa.animateDateRangeForward()
    
    def refresh_date_range_selector(self):
        self.cocoa.refreshDateRangeSelector()
    
    def refresh_reconciliation_button(self):
        self.cocoa.refreshReconciliationButton()
    
    def refresh_undo_actions(self):
        pass # We don't need this on the Cocoa side
    
    def show_account_reassign_panel(self):
        self.cocoa.showAccountReassignPanel()
    
    def show_balance_sheet(self):
        self.cocoa.showBalanceSheet()

    def show_bar_graph(self):
        self.cocoa.showBarGraph()
    
    def show_budget_table(self):
        self.cocoa.showBudgetTable()
    
    def show_custom_date_range_panel(self):
        self.cocoa.showCustomDateRangePanel()
    
    def show_entry_table(self):
        self.cocoa.showEntryTable()

    def show_line_graph(self):
        self.cocoa.showLineGraph()
    
    def show_income_statement(self):
        self.cocoa.showIncomeStatement()
    
    def show_message(self, message):
        self.cocoa.showMessage_(message)
    
    def show_schedule_table(self):
        self.cocoa.showScheduleTable()
    
    def show_transaction_table(self):
        self.cocoa.showTransactionTable()
    

class PyImportWindow(PyListener):
    py_class = ImportWindow
    
    @objc.signature('i@:i')
    def accountCountAtIndex_(self, index):
        return self.py.panes[index].count
    
    @objc.signature('@@:i')
    def accountNameAtIndex_(self, index):
        return self.py.panes[index].name
    
    @objc.signature('i@:')
    def canSwitchDayMonth(self):
        return self.py.can_switch_date_fields(DAY, MONTH)
    
    @objc.signature('i@:')
    def canSwitchDayYear(self):
        return self.py.can_switch_date_fields(DAY, YEAR)
    
    @objc.signature('i@:')
    def canSwitchMonthYear(self):
        return self.py.can_switch_date_fields(MONTH, YEAR)
    
    @objc.signature('@@:i')
    def closePaneAtIndex_(self, index):
        self.py.close_pane(index)
    
    def importSelectedPane(self):
        self.py.import_selected_pane()
    
    @objc.signature('i@:')
    def numberOfAccounts(self):
        return len(self.py.panes)
    
    @objc.signature('i@:')
    def selectedTargetAccountIndex(self):
        return self.py.selected_target_account_index
    
    @objc.signature('v@:i')
    def setSelectedAccountIndex_(self, index):
        self.py.selected_pane_index = index
    
    @objc.signature('v@:i')
    def setSelectedTargetAccountIndex_(self, index):
        self.py.selected_target_account_index = index
    
    @objc.signature('v@:i')
    def switchDayMonth_(self, applyToAll):
        return self.py.switch_date_fields(DAY, MONTH, apply_to_all=applyToAll)
    
    @objc.signature('v@:i')
    def switchDayYear_(self, applyToAll):
        return self.py.switch_date_fields(DAY, YEAR, apply_to_all=applyToAll)
    
    @objc.signature('v@:i')
    def switchMonthYear_(self, applyToAll):
        return self.py.switch_date_fields(MONTH, YEAR, apply_to_all=applyToAll)
    
    @objc.signature('v@:i')
    def switchDescriptionPayee_(self, applyToAll):
        return self.py.switch_description_payee(apply_to_all=applyToAll)
    
    def targetAccountNames(self):
        return self.py.target_account_names
    
    #--- Python -> Cocoa
    def close(self):
        self.cocoa.close()
    
    def close_selected_tab(self):
        self.cocoa.closeSelectedTab()
    
    def show(self):
        self.cocoa.show()
    
    def update_selected_pane(self):
        self.cocoa.updateSelectedPane()
    

class PyCSVImportOptions(PyWindowController):
    py_class = CSVOptions
    
    @objc.signature('@@:i')
    def columnNameAtIndex_(self, index):
        return self.py.get_column_name(index)
    
    def continueImport(self):
        self.py.continue_import()
    
    def deleteSelectedLayout(self):
        self.py.delete_selected_layout()
    
    def layoutNames(self):
        return self.py.layout_names
    
    @objc.signature('i@:i')
    def lineIsImported_(self, index):
        return not self.py.line_is_excluded(index)
    
    @objc.signature('i@:')
    def numberOfColumns(self):
        return len(self.py.columns)
    
    @objc.signature('i@:')
    def numberOfLines(self):
        return len(self.py.lines)
    
    def newLayout_(self, name):
        self.py.new_layout(name)
    
    def renameSelectedLayout_(self, newname):
        self.py.rename_selected_layout(newname)
    
    def selectedLayoutName(self):
        return self.py.layout.name
    
    @objc.signature('i@:')
    def selectedTargetIndex(self):
        return self.py.selected_target_index
    
    def selectLayout_(self, name):
        self.py.select_layout(name)
    
    @objc.signature('v@:ii')
    def setColumn_fieldForTag_(self, index, tag):
        field = CSV_FIELD_ORDER[tag]
        self.py.set_column_field(index, field)
    
    @objc.signature('v@:i')
    def setSelectedTargetIndex_(self, index):
        self.py.selected_target_index = index
    
    def targetAccountNames(self):
        return self.py.target_account_names
    
    @objc.signature('v@:i')
    def toggleLineExclusion_(self, index):
        self.py.set_line_excluded(index, not self.py.line_is_excluded(index))
    
    @objc.signature('@@:ii')
    def valueForRow_column_(self, row, column):
        return self.py.lines[row][column]
    
    #--- Python -> Cocoa
    def refresh_columns(self):
        self.cocoa.refreshColumns()
    
    def refresh_columns_name(self):
        self.cocoa.refreshColumnsName()
    
    def refresh_layout_menu(self):
        self.cocoa.refreshLayoutMenu()
    
    def refresh_lines(self):
        self.cocoa.refreshLines()
    
    def refresh_targets(self):
        self.cocoa.refreshTargets()
    
    def show(self):
        self.cocoa.show()
    
    def hide(self):
        self.cocoa.hide()
    

class PyImportTable(PyTable):
    py_class = ImportTable
    
    # pyparent is a PyImportWindow
    @objc.signature('v@:ii')
    def bindRow_to_(self, source_index, dest_index):
        self.py.bind(source_index, dest_index)
    
    @objc.signature('i@:ii')
    def canBindRow_to_(self, source_index, dest_index):
        return self.py.can_bind(source_index, dest_index)
    
    @objc.signature('v@:i')
    def unbindRow_(self, index):
        self.py.unbind(index)
    

class PyDateWidget(NSObject):
    def init(self):
        self = NSObject.init(self)
        NSDateFormatter.setDefaultFormatterBehavior_(NSDateFormatterBehavior10_4)
        f = NSDateFormatter.alloc().init()
        f.setDateStyle_(NSDateFormatterShortStyle)
        f.setTimeStyle_(NSDateFormatterNoStyle)
        self.date_format = clean_format(f.dateFormat())
        self.w = DateWidget(self.date_format)
        return self
    
    def increase(self):
        self.w.increase()
    
    def decrease(self):
        self.w.decrease()
    
    def left(self):
        self.w.left()
    
    def right(self):
        self.w.right()
    
    def backspace(self):
        self.w.backspace()
    
    def exit(self):
        self.w.exit()
    
    def type_(self, something):
        self.w.type(something)
    
    def setDate_(self, str_date):
        self.w.text = str_date
    
    def text(self):
        return self.w.text
    
    def selection(self):
        return self.w.selection
    

#--- Printing

class PyPrintView(NSObject):
    py_class = PrintView
    
    # The parent of the PyPrintView is a Document GUI object (*not* the document itself!)
    def initWithPyParent_(self, pyparent):
        self = NSObject.init(self)
        self.py = self.py_class(pyparent.py)
        return self
    
    def startDate(self):
        return self.py.start_date
    
    def endDate(self):
        return self.py.end_date
    

class PySplitPrint(PyPrintView):
    @objc.signature('i@:i')
    def splitCountAtRow_(self, row):
        return self.py.split_count_at_row(row)
    
    @objc.signature('@@:ii')
    def splitValuesAtRow_splitRow_(self, row, split_row):
        return self.py.split_values(row, split_row)
    

class PyTransactionPrint(PySplitPrint):
    py_class = TransactionPrint

class PyEntryPrint(PySplitPrint):
    py_class = EntryPrint
