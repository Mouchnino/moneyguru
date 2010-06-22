# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# index_path are arrays of int. Convert them from NSIndexPath with cocoalib.Utils.indexPath2Array
import logging

from hsutil.cocoa import install_exception_hook, pythonify
from hsutil.cocoa.inter import signature, PyGUIObject, PyTable, PyOutline, PyRegistrable
from hsutil.cocoa.objcmin import (NSObject, NSUserDefaults, NSSearchPathForDirectoriesInDomains,
    NSCachesDirectory, NSUserDomainMask, NSLocale, NSLocaleCurrencyCode, NSDateFormatter,
    NSDateFormatterBehavior10_4, NSDateFormatterShortStyle, NSDateFormatterNoStyle,
    NSNumberFormatter, NSNumberFormatterBehavior10_4)
from hsutil.path import Path
from hsutil.currency import Currency, USD
from hsutil.misc import nonone
from hsutil.reg import InvalidCodeError

from core.app import Application
from core.document import Document, FilterType
from core.exception import FileFormatError
from core.gui.account_balance_graph import AccountBalanceGraph
from core.gui.account_flow_graph import AccountFlowGraph
from core.gui.account_lookup import AccountLookup
from core.gui.account_panel import AccountPanel
from core.gui.account_pie_chart import AssetsPieChart, LiabilitiesPieChart, IncomePieChart, ExpensesPieChart
from core.gui.account_reassign_panel import AccountReassignPanel
from core.gui.account_view import AccountView
from core.gui.balance_sheet import BalanceSheet
from core.gui.budget_table import BudgetTable
from core.gui.budget_panel import BudgetPanel
from core.gui.budget_view import BudgetView
from core.gui.csv_options import CSVOptions, FIELD_ORDER as CSV_FIELD_ORDER
from core.gui.completable_edit import CompletableEdit
from core.gui.completion_lookup import CompletionLookup
from core.gui.custom_date_range_panel import CustomDateRangePanel
from core.gui.date_range_selector import DateRangeSelector
from core.gui.date_widget import DateWidget
from core.gui.entry_print import EntryPrint
from core.gui.empty_view import EmptyView
from core.gui.entry_table import EntryTable
from core.gui.filter_bar import TransactionFilterBar, EntryFilterBar
from core.gui.income_statement import IncomeStatement
from core.gui.import_table import ImportTable
from core.gui.import_window import ImportWindow, DAY, MONTH, YEAR
from core.gui.main_window import MainWindow
from core.gui.mass_edition_panel import MassEditionPanel
from core.gui.net_worth_graph import NetWorthGraph
from core.gui.networth_view import NetWorthView
from core.gui.print_view import PrintView
from core.gui.profit_graph import ProfitGraph
from core.gui.profit_view import ProfitView
from core.gui.schedule_panel import SchedulePanel
from core.gui.schedule_table import ScheduleTable
from core.gui.schedule_view import ScheduleView
from core.gui.search_field import SearchField
from core.gui.split_table import SplitTable
from core.gui.transaction_panel import TransactionPanel
from core.gui.transaction_print import TransactionPrint
from core.gui.transaction_table import TransactionTable
from core.gui.transaction_view import TransactionView
from core.model.date import clean_format

# These imports below are a workaround for py2app, which doesn't like relative imports
import csv
from hsutil import job
from core import const
from core.gui import base, chart, graph, report, table
from core.loader import base, csv, native, ofx, qif
from core.model import (account, amount, currency, date, oven, recurrence, transaction,
    transaction_list, completion, undo)

class PyMoneyGuruApp(PyRegistrable):
    def initWithCocoa_(self, cocoa):
        super(PyMoneyGuruApp, self).init()
        self.cocoa = cocoa
        LOGGING_LEVEL = logging.DEBUG if NSUserDefaults.standardUserDefaults().boolForKey_('debug') else logging.WARNING
        logging.basicConfig(level=LOGGING_LEVEL, format='%(levelname)s %(message)s')
        logging.debug('started in debug mode')
        install_exception_hook()
        std_caches_path = Path(NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, True)[0])
        cache_path = std_caches_path + 'moneyGuru'
        currency_code = nonone(NSLocale.currentLocale().objectForKey_(NSLocaleCurrencyCode), 'USD')
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
    
    def free(self): # see PyGUIObject
        if hasattr(self, 'cocoa'):
            del self.cocoa
    
    def get_default(self, key_name):
        raw = NSUserDefaults.standardUserDefaults().objectForKey_(key_name)
        result = pythonify(raw)
        return result
    
    def set_default(self, key_name, value):
        NSUserDefaults.standardUserDefaults().setObject_forKey_(value, key_name)
    
    #--- Preferences
    @signature('i@:')
    def firstWeekday(self):
        return self.py.first_weekday
    
    @signature('v@:i')
    def setFirstWeekday_(self, weekday):
        self.py.first_weekday = weekday
    
    @signature('i@:')
    def aheadMonths(self):
        return self.py.ahead_months
    
    @signature('v@:i')
    def setAheadMonths_(self, months):
        self.py.ahead_months = months
    
    # The selector in the pref pane is 0-based, the py side's pref is 1-based
    @signature('i@:')
    def yearStartMonth(self):
        return self.py.year_start_month - 1
    
    @signature('v@:i')
    def setYearStartMonth_(self, month):
        self.py.year_start_month = month + 1
    
    @signature('i@:')
    def autoSaveInterval(self):
        return self.py.autosave_interval
    
    @signature('v@:i')
    def setAutoSaveInterval_(self, minutes):
        self.py.autosave_interval = minutes
    
    @signature('c@:')
    def autoDecimalPlace(self):
        return self.py.auto_decimal_place
    
    @signature('v@:c')
    def setAutoDecimalPlace_(self, value):
        self.py.auto_decimal_place = value
    
    #---Registration
    def appName(self):
        return self.py.APP_NAME
    
    #--- Python -> Cocoa
    def setup_as_registered(self):
        self.cocoa.setupAsRegistered()
    

class PyDocument(NSObject):
    def initWithCocoa_pyParent_(self, cocoa, pyparent):
        super(PyDocument, self).init()
        self.cocoa = cocoa
        self.py = Document(self, pyparent.py)
        self.py.connect()
        return self
    
    #--- Undo
    @signature('c@:')
    def canUndo(self):
        return self.py.can_undo()
    
    def undoDescription(self):
        return self.py.undo_description()
    
    def undo(self):
        self.py.undo()
    
    @signature('c@:')
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
    
    @signature('c@:')
    def isDirty(self):
        return self.py.is_dirty()
    
    def stopEdition(self):
        self.py.stop_edition()
    
    @signature('i@:')
    def transactionCount(self):
        return len(self.py.transactions)
    
    def close(self):
        self.py.close()
        self.py.disconnect()
    
    # temporary
    @signature('i@:')
    def isRegistered(self):
        return self.py.app.registered
    
    def free(self): # see PyGUIObject
        if hasattr(self, 'cocoa'):
            del self.cocoa
    
    #--- Python -> Cocoa
    def query_for_schedule_scope(self):
        return self.cocoa.queryForScheduleScope()
    

#--- Root classes
class PyListener(PyGUIObject):
    def connect(self):
        self.py.connect()
    
    def disconnect(self):
        self.py.disconnect()
    
    def free(self):
        self.disconnect()
        PyGUIObject.free(self)
    

class PyGUIContainer(PyListener):
    def setChildren_(self, children):
        self.py.set_children([child.py for child in children])
    

class PyWindowController(PyListener):
    pass

class PyTableWithDate(PyTable):
    @signature('c@:')
    def isEditedRowInTheFuture(self):
        if self.py.edited is None:
            return False
        return self.py.edited.is_date_in_future()
    
    @signature('c@:')
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
    @signature('f@:')
    def xMin(self):
        return self.py.xmin

    @signature('f@:')
    def xMax(self):
        return self.py.xmax
    
    @signature('f@:')
    def yMin(self):
        return self.py.ymin
    
    @signature('f@:')
    def yMax(self):
        return self.py.ymax
    
    @signature('f@:')
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
    

class PyReport(PyOutline):
    @signature('c@:')
    def canDeleteSelected(self):
        return self.py.can_delete()
    
    def deleteSelected(self):
        self.py.delete()
    
    @signature('c@:@@')
    def canMovePath_toPath_(self, source_path, dest_path):
        return self.py.can_move(source_path, dest_path)
    
    def movePath_toPath_(self, source_path, dest_path):
        self.py.move(source_path, dest_path)
    
    def showSelectedAccount(self):
        self.py.show_selected_account()
    
    @signature('c@:')
    def canShowSelectedAccount(self):
        return self.py.can_show_selected_account
    
    def toggleExcluded(self):
        self.py.toggle_excluded()
    
    def expandPath_(self, path):
        self.py.expand_node(self.py.get_node(path))
        
    def collapsePath_(self, path):
        self.py.collapse_node(self.py.get_node(path))
    
    def expandedPaths(self):
        return self.py.expanded_paths
    

class PyPanel(PyGUIObject):
    def savePanel(self):
        self.py.save()
    
    # Python --> Cocoa
    def pre_load(self):
        self.cocoa.preLoad()
    
    def post_load(self):
        self.cocoa.postLoad()
    
    def pre_save(self):
        self.cocoa.preSave()
    

#--- Views
class PyNetWorthView(PyGUIContainer):
    py_class = NetWorthView

class PyProfitView(PyGUIContainer):
    py_class = ProfitView

class PyTransactionView(PyGUIContainer):
    py_class = TransactionView

class PyAccountView(PyGUIContainer):
    py_class = AccountView

    @signature('c@:')
    def canToggleReconciliationMode(self):
        return self.py.can_toggle_reconciliation_mode
    
    @signature('c@:')
    def inReconciliationMode(self):
        return self.py.reconciliation_mode
    
    def toggleReconciliationMode(self):
        self.py.toggle_reconciliation_mode()
    
    #Python --> Cocoa
    def refresh_reconciliation_button(self):
        self.cocoa.refreshReconciliationButton()
    
    def show_bar_graph(self):
        self.cocoa.showBarGraph()
    
    def show_line_graph(self):
        self.cocoa.showLineGraph()
    

class PyBudgetView(PyGUIContainer):
    py_class = BudgetView

class PyScheduleView(PyGUIContainer):
    py_class = ScheduleView

class PyEmptyView(PyGUIContainer):
    py_class = EmptyView
    
    @signature('v@:i')
    def selectPaneType_(self, paneType):
        self.py.select_pane_type(paneType)
    

#--- GUI layer classes

class PyBalanceSheet(PyReport):
    py_class = BalanceSheet

class PyIncomeStatement(PyReport):
    py_class = IncomeStatement

class PyEntryTable(PyTableWithDate):
    py_class = EntryTable

    @signature('c@:@i')
    def canMoveRows_to_(self, rows, position):
        return self.py.can_move(list(rows), position)

    @signature('c@:i')
    def canReconcileEntryAtRow_(self, row):
        return self.py[row].can_reconcile()
    
    @signature('c@:i')
    def isBalanceNegativeAtRow_(self, row):
        return self.py[row].is_balance_negative()
    
    @signature('c@:i')
    def isBoldAtRow_(self, row):
        return self.py[row].is_bold
    
    @signature('v@:@i')
    def moveRows_to_(self, rows, position):
        self.py.move(list(rows), position)

    @signature('c@:')
    def shouldShowBalanceColumn(self):
        return self.py.should_show_balance_column()
    
    def showTransferAccount(self):
        self.py.show_transfer_account()
    
    def toggleReconciled(self):
        self.py.toggle_reconciled()
    
    @signature('v@:i')
    def toggleReconciledAtRow_(self, row_index):
        self.py[row_index].toggle_reconciled()
    

class PyTransactionTable(PyTableWithDate):
    py_class = TransactionTable
    
    @signature('c@:i')
    def isBoldAtRow_(self, row):
        return self.py[row].is_bold
    
    @signature('c@:@i')
    def canMoveRows_to_(self, rows, position):
        return self.py.can_move(list(rows), position)
    
    @signature('v@:@i')
    def moveRows_to_(self, rows, position):
        self.py.move(list(rows), position)
    
    def showFromAccount(self):
        self.py.show_from_account()
    
    def showToAccount(self):
        self.py.show_to_account()
    

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
    

class PyFilterBarBase(PyListener):
    def filterType(self):
        result = 'all'
        if self.py.filter_type is FilterType.Unassigned:
            result = 'unassigned'
        elif self.py.filter_type is FilterType.Income:
            result = 'income'
        elif self.py.filter_type is FilterType.Expense:
            result = 'expense'
        elif self.py.filter_type is FilterType.Transfer:
            result = 'transfer'
        elif self.py.filter_type is FilterType.Reconciled:
            result = 'reconciled'
        elif self.py.filter_type is FilterType.NotReconciled:
            result = 'not_reconciled'
        return result
    
    def setFilterType_(self, filter_type):
        value = None
        if filter_type == 'unassigned':
            value = FilterType.Unassigned
        elif filter_type == 'income':
            value = FilterType.Income
        elif filter_type == 'expense':
            value = FilterType.Expense
        elif filter_type == 'transfer':
            value = FilterType.Transfer
        elif filter_type == 'reconciled':
            value = FilterType.Reconciled
        elif filter_type == 'not_reconciled':
            value = FilterType.NotReconciled
        self.py.filter_type = value
    

class PyTransactionFilterBar(PyFilterBarBase):
    py_class = TransactionFilterBar

class PyEntryFilterBar(PyFilterBarBase):
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
    
    @signature('i@:')
    def typeIndex(self):
        return self.py.type_index
    
    @signature('@@:i')
    def setTypeIndex_(self, index):
        self.py.type_index = index
    
    @signature('i@:')
    def currencyIndex(self):
        return self.py.currency_index
    
    @signature('@@:i')
    def setCurrencyIndex_(self, index):
        self.py.currency_index = index
    
    def accountNumber(self):
        return self.py.account_number
    
    def setAccountNumber_(self, accountNumber):
        self.py.account_number = accountNumber
    
    def availableCurrencies(self):
        return ['%s - %s' % (currency.code, currency.name) for currency in Currency.all]
    

class PySplitTable(PyTable):
    py_class = SplitTable
    # pyparent is a PyTransactionPanel
    
    @signature('v@:ii')
    def moveSplitFromRow_toRow_(self, from_row, to_row):
        self.py.move_split(from_row, to_row)
    

class PyPanelWithTransaction(PyPanel):
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
    
    def notes(self):
        return self.py.notes
    
    def setNotes_(self, value):
        self.py.notes = value
    
    @signature('c@:')
    def isMultiCurrency(self):
        return self.py.is_multi_currency
    
    #--- Python -> Cocoa
    def refresh_for_multi_currency(self):
        self.cocoa.refreshForMultiCurrency()
    

class PyTransactionPanel(PyPanelWithTransaction):
    py_class = TransactionPanel

    def mctBalance(self):
        self.py.mct_balance()
    
    def date(self):
        return self.py.date
    
    def setDate_(self, value):
        self.py.date = value
    

class PyMassEditionPanel(PyPanel):
    py_class = MassEditionPanel

    def availableCurrencies(self):
        return ['%s - %s' % (currency.code, currency.name) for currency in Currency.all]
    
    @signature('c@:')
    def canChangeAccounts(self):
        return self.py.can_change_accounts
    
    @signature('c@:')
    def canChangeAmount(self):
        return self.py.can_change_amount
    
    @signature('c@:')
    def dateEnabled(self):
        return self.py.date_enabled
    
    @signature('v@:c')
    def setDateEnabled_(self, value):
        self.py.date_enabled = value
    
    @signature('c@:')
    def descriptionEnabled(self):
        return self.py.description_enabled
    
    @signature('v@:c')
    def setDescriptionEnabled_(self, value):
        self.py.description_enabled = value
    
    @signature('c@:')
    def payeeEnabled(self):
        return self.py.payee_enabled
    
    @signature('v@:c')
    def setPayeeEnabled_(self, value):
        self.py.payee_enabled = value
    
    @signature('c@:')
    def checknoEnabled(self):
        return self.py.checkno_enabled
    
    @signature('v@:c')
    def setChecknoEnabled_(self, value):
        self.py.checkno_enabled = value
    
    @signature('c@:')
    def fromEnabled(self):
        return self.py.from_enabled
    
    @signature('v@:c')
    def setFromEnabled_(self, value):
        self.py.from_enabled = value
    
    @signature('c@:')
    def toEnabled(self):
        return self.py.to_enabled
    
    @signature('v@:c')
    def setToEnabled_(self, value):
        self.py.to_enabled = value
    
    @signature('c@:')
    def amountEnabled(self):
        return self.py.amount_enabled
    
    @signature('v@:c')
    def setAmountEnabled_(self, value):
        self.py.amount_enabled = value
    
    @signature('c@:')
    def currencyEnabled(self):
        return self.py.currency_enabled
    
    @signature('v@:c')
    def setCurrencyEnabled_(self, value):
        self.py.currency_enabled = value
    
    def date(self):
        return self.py.date
    
    @signature('v@:@')
    def setDate_(self, value):
        self.py.date = value
    
    def description(self):
        return self.py.description
    
    @signature('v@:@')
    def setDescription_(self, value):
        self.py.description = value
    
    def payee(self):
        return self.py.payee
    
    @signature('v@:@')
    def setPayee_(self, value):
        self.py.payee = value
    
    def checkno(self):
        return self.py.checkno
    
    @signature('v@:@')
    def setCheckno_(self, value):
        self.py.checkno = value
    
    def fromAccount(self): # We cannot use the underscore to escape the kw. It messes with pyobjc
        return self.py.from_
    
    @signature('v@:@')
    def setFromAccount_(self, value):
        self.py.from_ = value
    
    def to(self):
        return self.py.to
    
    @signature('v@:@')
    def setTo_(self, value):
        self.py.to = value
    
    def amount(self):
        return self.py.amount
    
    @signature('v@:@')
    def setAmount_(self, value):
        self.py.amount = value
    
    @signature('i@:')
    def currencyIndex(self):
        return self.py.currency_index
    
    @signature('v@:i')
    def setCurrencyIndex_(self, value):
        self.py.currency_index = value
    

class PySchedulePanel(PyPanelWithTransaction):
    py_class = SchedulePanel
    
    def startDate(self):
        return self.py.start_date
    
    def setStartDate_(self, value):
        self.py.start_date = value
    
    def stopDate(self):
        return self.py.stop_date
    
    def setStopDate_(self, value):
        self.py.stop_date = value
    
    @signature('i@:')
    def repeatEvery(self):
        return self.py.repeat_every
    
    @signature('v@:i')
    def setRepeatEvery_(self, value):
        self.py.repeat_every = value
    
    def repeatEveryDesc(self):
        return self.py.repeat_every_desc
    
    @signature('i@:')
    def repeatTypeIndex(self):
        return self.py.repeat_type_index
    
    @signature('v@:i')
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
    
    @signature('i@:')
    def repeatEvery(self):
        return self.py.repeat_every
    
    @signature('v@:i')
    def setRepeatEvery_(self, value):
        self.py.repeat_every = value
    
    def repeatEveryDesc(self):
        return self.py.repeat_every_desc
    
    @signature('i@:')
    def repeatTypeIndex(self):
        return self.py.repeat_type_index
    
    @signature('v@:i')
    def setRepeatTypeIndex_(self, value):
        self.py.repeat_type_index = value
    
    @signature('i@:')
    def accountIndex(self):
        return self.py.account_index
    
    @signature('v@:i')
    def setAccountIndex_(self, value):
        self.py.account_index = value
    
    @signature('i@:')
    def targetIndex(self):
        return self.py.target_index
    
    @signature('v@:i')
    def setTargetIndex_(self, value):
        self.py.target_index = value
    
    def amount(self):
        return self.py.amount
    
    def setAmount_(self, value):
        self.py.amount = value
    
    def notes(self):
        return self.py.notes
    
    def setNotes_(self, value):
        self.py.notes = value
    
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
    

class PyCustomDateRangePanel(PyPanel):
    py_class = CustomDateRangePanel
    
    def startDate(self):
        return self.py.start_date
    
    def setStartDate_(self, value):
        self.py.start_date = value
    
    def endDate(self):
        return self.py.end_date
    
    def setEndDate_(self, value):
        self.py.end_date = value
    
    @signature('i@:')
    def slotIndex(self):
        return self.py.slot_index
    
    @signature('v@:i')
    def setSlotIndex_(self, index):
        self.py.slot_index = index
    
    def slotName(self):
        return self.py.slot_name
    
    def setSlotName_(self, name):
        self.py.slot_name = name
    

class PyAccountReassignPanel(PyPanel):
    py_class = AccountReassignPanel
    
    def availableAccounts(self):
        return self.py.available_accounts
    
    @signature('i@:')
    def accountIndex(self):
        return self.py.account_index
    
    @signature('v@:i')
    def setAccountIndex_(self, value):
        self.py.account_index = value
    

class PyAccountBalanceGraph(PyGraph):
    py_class = AccountBalanceGraph

class PyNetWorthGraph(PyGraph):
    py_class = NetWorthGraph

class PyAccountFlowGraph(PyGraph):
    py_class = AccountFlowGraph

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

class PyMainWindow(PyGUIContainer):
    py_class = MainWindow
    
    def selectNextView(self):
        self.py.select_next_view()
    
    def selectPreviousView(self):
        self.py.select_previous_view()
    
    @signature('i@:')
    def currentPaneIndex(self):
        return self.py.current_pane_index
    
    @signature('v@:i')
    def setCurrentPaneIndex_(self, index):
        self.py.current_pane_index = index
    
    @signature('i@:')
    def paneCount(self):
        return self.py.pane_count
    
    @signature('@@:i')
    def paneLabelAtIndex_(self, index):
        return self.py.pane_label(index)
    
    @signature('i@:i')
    def paneTypeAtIndex_(self, index):
        return self.py.pane_type(index)
    
    @signature('v@:i')
    def showPaneOfType_(self, pane_type):
        self.py.select_pane_of_type(pane_type)
    
    @signature('v@:i')
    def closePaneAtIndex_(self, index):
        self.py.close_pane(index)
    
    @signature('v@:ii')
    def movePaneAtIndex_toIndex_(self, pane_index, dest_index):
        self.py.move_pane(pane_index, dest_index)
    
    def newTab(self):
        self.py.new_tab()
    
    def showAccount(self):
        self.py.show_account()
    
    def navigateBack(self):
        self.py.navigate_back()
    
    def jumpToAccount(self):
        self.py.jump_to_account()
    
    #--- Item Management
    def deleteItem(self):
        self.py.delete_item()
    
    def duplicateItem(self):
        self.py.duplicate_item()
    
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
    
    #--- Other
    def statusLine(self):
        return self.py.status_line
    
    #--- Python -> Cocoa
    def change_current_pane(self):
        self.cocoa.changeSelectedPane()
    
    def refresh_panes(self):
        self.cocoa.refreshPanes()
    
    def refresh_undo_actions(self):
        pass # We don't need this on the Cocoa side
    
    def show_custom_date_range_panel(self):
        self.cocoa.showCustomDateRangePanel()
    
    def refresh_status_line(self):
        self.cocoa.refreshStatusLine()
    
    def show_message(self, message):
        self.cocoa.showMessage_(message)
    
    def view_closed(self, index):
        self.cocoa.viewClosedAtIndex_(index)
    

class PyImportWindow(PyListener):
    py_class = ImportWindow
    
    @signature('i@:i')
    def accountCountAtIndex_(self, index):
        return self.py.panes[index].count
    
    @signature('@@:i')
    def accountNameAtIndex_(self, index):
        return self.py.panes[index].name
    
    @signature('c@:')
    def canSwitchDayMonth(self):
        return self.py.can_switch_date_fields(DAY, MONTH)
    
    @signature('c@:')
    def canSwitchDayYear(self):
        return self.py.can_switch_date_fields(DAY, YEAR)
    
    @signature('c@:')
    def canSwitchMonthYear(self):
        return self.py.can_switch_date_fields(MONTH, YEAR)
    
    @signature('@@:i')
    def closePaneAtIndex_(self, index):
        self.py.close_pane(index)
    
    def importSelectedPane(self):
        self.py.import_selected_pane()
    
    @signature('i@:')
    def numberOfAccounts(self):
        return len(self.py.panes)
    
    @signature('i@:')
    def selectedTargetAccountIndex(self):
        return self.py.selected_target_account_index
    
    @signature('v@:i')
    def setSelectedAccountIndex_(self, index):
        self.py.selected_pane_index = index
    
    @signature('v@:i')
    def setSelectedTargetAccountIndex_(self, index):
        self.py.selected_target_account_index = index
    
    @signature('v@:c')
    def switchDayMonth_(self, applyToAll):
        return self.py.switch_date_fields(DAY, MONTH, apply_to_all=applyToAll)
    
    @signature('v@:c')
    def switchDayYear_(self, applyToAll):
        return self.py.switch_date_fields(DAY, YEAR, apply_to_all=applyToAll)
    
    @signature('v@:c')
    def switchMonthYear_(self, applyToAll):
        return self.py.switch_date_fields(MONTH, YEAR, apply_to_all=applyToAll)
    
    @signature('v@:c')
    def switchDescriptionPayee_(self, applyToAll):
        return self.py.switch_description_payee(apply_to_all=applyToAll)
    
    def targetAccountNames(self):
        return self.py.target_account_names
    
    #--- Python -> Cocoa
    def close(self):
        self.cocoa.close()
    
    def close_selected_tab(self):
        self.cocoa.closeSelectedTab()
    
    def refresh_tabs(self):
        self.cocoa.refreshTabs()
    
    def refresh_target_accounts(self):
        self.cocoa.refreshTargetAccounts()
    
    def show(self):
        self.cocoa.show()
    
    def update_selected_pane(self):
        self.cocoa.updateSelectedPane()
    

class PyCSVImportOptions(PyWindowController):
    py_class = CSVOptions
    
    @signature('@@:i')
    def columnNameAtIndex_(self, index):
        return self.py.get_column_name(index)
    
    def continueImport(self):
        self.py.continue_import()
    
    def deleteSelectedLayout(self):
        self.py.delete_selected_layout()
    
    def fieldSeparator(self):
        return self.py.field_separator
    
    def layoutNames(self):
        return self.py.layout_names
    
    @signature('c@:i')
    def lineIsImported_(self, index):
        return not self.py.line_is_excluded(index)
    
    @signature('i@:')
    def numberOfColumns(self):
        return len(self.py.columns)
    
    @signature('i@:')
    def numberOfLines(self):
        return len(self.py.lines)
    
    def newLayout_(self, name):
        self.py.new_layout(name)
    
    def renameSelectedLayout_(self, newname):
        self.py.rename_selected_layout(newname)
    
    def rescan(self):
        self.py.rescan()
    
    def selectedLayoutName(self):
        return self.py.layout.name
    
    @signature('i@:')
    def selectedTargetIndex(self):
        return self.py.selected_target_index
    
    def selectLayout_(self, name):
        self.py.select_layout(name)
    
    @signature('v@:ii')
    def setColumn_fieldForTag_(self, index, tag):
        field = CSV_FIELD_ORDER[tag]
        self.py.set_column_field(index, field)
    
    def setFieldSeparator_(self, fieldSep):
        self.py.field_separator = fieldSep
    
    @signature('v@:i')
    def setSelectedTargetIndex_(self, index):
        self.py.selected_target_index = index
    
    def targetAccountNames(self):
        return self.py.target_account_names
    
    @signature('v@:i')
    def toggleLineExclusion_(self, index):
        self.py.set_line_excluded(index, not self.py.line_is_excluded(index))
    
    @signature('@@:ii')
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
    
    def show_message(self, msg):
        self.cocoa.showMessage_(msg)
    

class PyImportTable(PyTable):
    py_class = ImportTable
    
    # pyparent is a PyImportWindow
    @signature('v@:ii')
    def bindRow_to_(self, source_index, dest_index):
        self.py.bind(source_index, dest_index)
    
    @signature('c@:ii')
    def canBindRow_to_(self, source_index, dest_index):
        return self.py.can_bind(source_index, dest_index)
    
    @signature('c@:')
    def isTwoSided(self):
        return self.py.is_two_sided
    
    @signature('v@:')
    def toggleImportStatus(self):
        self.py.toggle_import_status()
    
    @signature('v@:i')
    def unbindRow_(self, index):
        self.py.unbind(index)
    

class PyLookup(PyGUIObject):
    def go(self):
        self.py.go()
    
    def names(self):
        return self.py.names
    
    def searchQuery(self):
        return self.py.search_query
    
    def setSearchQuery_(self, query):
        self.py.search_query = query
    
    @signature('i@:')
    def selectedIndex(self):
        return self.py.selected_index
    
    @signature('v@:i')
    def setSelectedIndex_(self, index):
        self.py.selected_index = index
    
    #--- Python --> Cocoa
    def show(self):
        self.cocoa.show()
    
    def hide(self):
        self.cocoa.hide()
    

class PyAccountLookup(PyLookup):
    py_class = AccountLookup

class PyCompletionLookup(PyLookup):
    py_class = CompletionLookup

class PyDateWidget(NSObject):
    def init(self):
        super(PyDateWidget, self).init()
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
    

class PyCompletableEdit(NSObject):
    def initWithCocoa_pyParent_(self, cocoa, pyparent):
        super(PyCompletableEdit, self).init()
        self.py = CompletableEdit(view=self, mainwindow=pyparent.py)
        self.cocoa = cocoa
        return self
    
    def setAttrname_(self, attrname):
        self.py.attrname = attrname
    
    def text(self):
        return self.py.text
    
    def setText_(self, value):
        # Don't send value directly to the py side! NSString are mutable and weird stuff will
        # happen if you do that!
        self.py.text = unicode(value)
    
    def completion(self):
        return self.py.completion
    
    def commit(self):
        self.py.commit()
    
    def down(self):
        self.py.down()
    
    def up(self):
        self.py.up()
    
    def lookup(self):
        self.py.lookup()
    
    # Python --> Cocoa
    def refresh(self):
        self.cocoa.refresh()
    

class PyDateRangeSelector(PyGUIObject):
    py_class = DateRangeSelector
    
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
    
    def selectAllTransactionsRange(self):
        self.py.select_all_transactions_range()
    
    def selectCustomDateRange(self):
        self.py.select_custom_date_range()
    
    @signature('v@:i')
    def selectSavedRange_(self, slot):
        self.py.select_saved_range(slot)
    
    def display(self):
        return self.py.display
    
    @signature('c@:')
    def canNavigate(self):
        return self.py.can_navigate
    
    def customRangeNames(self):
        return self.py.custom_range_names
    
    #--- Python -> Cocoa
    def animate_backward(self):
        self.cocoa.animateBackward()
    
    def animate_forward(self):
        self.cocoa.animateForward()
    
    def refresh(self):
        self.cocoa.refresh()
    
    def refresh_custom_ranges(self):
        self.cocoa.refreshCustomRanges()
    

#--- Printing

class PyPrintView(NSObject):
    py_class = PrintView
    
    # The parent of the PyPrintView is a Document GUI object (*not* the document itself!)
    def initWithPyParent_(self, pyparent):
        super(PyPrintView, self).init()
        self.py = self.py_class(pyparent.py)
        return self
    
    def startDate(self):
        return self.py.start_date
    
    def endDate(self):
        return self.py.end_date
    

class PySplitPrint(PyPrintView):
    @signature('i@:i')
    def splitCountAtRow_(self, row):
        return self.py.split_count_at_row(row)
    
    @signature('@@:ii')
    def splitValuesAtRow_splitRow_(self, row, split_row):
        return self.py.split_values(row, split_row)
    

class PyTransactionPrint(PySplitPrint):
    py_class = TransactionPrint

class PyEntryPrint(PySplitPrint):
    py_class = EntryPrint
