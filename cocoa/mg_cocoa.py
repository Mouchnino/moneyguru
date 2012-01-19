# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# index_path are arrays of int. Convert them from NSIndexPath with cocoalib.Utils.indexPath2Array
import logging
import objc # import needed for dependency collection to work well
from objp.util import pyref, dontwrap

from cocoa import install_exception_hook, proxy
from cocoa.inter import (signature, subproxy, PyGUIObject, PyTable, PyOutline, PyFairware,
    PySelectableList)
from cocoa.inter2 import PyGUIObject2, GUIObjectView, PyTable2, PyColumns2
from cocoa.objcmin import (NSObject, NSLocale, NSLocaleCurrencyCode, NSDateFormatter,
    NSDateFormatterBehavior10_4, NSDateFormatterShortStyle, NSDateFormatterNoStyle,
    NSNumberFormatter, NSNumberFormatterBehavior10_4)
from hscommon.currency import Currency, USD
from hscommon.path import Path
from hscommon.util import nonone

# Set translation func. This has to be set before core modules are initialized
import hscommon.trans
hscommon.trans.install_gettext_trans_under_cocoa()

from core.app import Application
from core.document import Document, FilterType
from core.exception import FileFormatError
from core.gui.csv_options import CSVOptions, FIELD_ORDER as CSV_FIELD_ORDER, \
    SUPPORTED_ENCODINGS as CSV_SUPPORTED_ENCODINGS
from core.gui.date_widget import DateWidget
from core.gui.import_window import ImportWindow
from core.gui.main_window import MainWindow
from core.gui.print_view import PrintView
from core.gui.transaction_print import TransactionPrint, EntryPrint
from core.model.date import clean_format

# This is a temporary, very hackish way of getting a PyObject* reference out of a pyobjc-based
# instance. I couldn't figure out how to directly get it. When objp conversion is complete, we
# won't need this anymore.
class PyHack(NSObject):
    def setRef_(self, ref):
        import __main__
        __main__.HACK_INSTANCE = ref.py


class PyMoneyGuruApp(PyFairware):
    def initWithCocoa_(self, cocoa):
        super(PyMoneyGuruApp, self).init()
        self.cocoa = cocoa
        LOGGING_LEVEL = logging.DEBUG if proxy.prefValue_('debug') else logging.WARNING
        logging.basicConfig(level=LOGGING_LEVEL, format='%(levelname)s %(message)s')
        logging.debug('started in debug mode')
        install_exception_hook()
        std_caches_path = Path(proxy.getCachePath())
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
    
    #--- Public
    @signature('c@:')
    def isFirstRun(self):
        return self.py.is_first_run
    
    #--- Preferences
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
            return str(e)
    
    def saveToFile_(self, filename):
        self.py.save_to_xml(filename)
    
    def import_(self, filename):
        try:
            self.py.parse_file_for_import(filename)
        except FileFormatError as e:
            return str(e)
    
    @signature('c@:')
    def isDirty(self):
        return self.py.is_dirty()
    
    def stopEdition(self):
        self.py.stop_edition()
    
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
    
class PyListener2(PyGUIObject2):
    def connect(self):
        self.model.connect()
    
    def disconnect(self):
        self.model.disconnect()
    

class PyGUIContainer(PyListener):
    def setChildren_(self, children):
        self.py.set_children([child.py for child in children])
    

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
    def canMovePaths_toPath_(self, source_paths, dest_path):
        return self.py.can_move(source_paths, dest_path)
    
    def movePaths_toPath_(self, source_paths, dest_path):
        self.py.move(source_paths, dest_path)
    
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
    
    def selectionAsCSV(self):
        return self.py.selection_as_csv()
    
    # Python --> Cocoa
    def refresh_expanded_paths(self):
        self.cocoa.refreshExpandedPaths()
    

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
    
#--- GUI layer classes

class PyEntryTable(PyTableWithDate):
    completableEdit = subproxy('completableEdit', 'completable_edit', PyGUIObject)
    
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

    def showTransferAccount(self):
        self.py.show_transfer_account()
    
    def toggleReconciled(self):
        self.py.toggle_reconciled()
    
    @signature('v@:i')
    def toggleReconciledAtRow_(self, row_index):
        self.py[row_index].toggle_reconciled()
    

class PyTransactionTable(PyTableWithDate):
    completableEdit = subproxy('completableEdit', 'completable_edit', PyGUIObject)
    
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
    def editItem(self):
        self.py.edit()
    

class PyBudgetTable(PyTable):
    def editItem(self):
        self.py.edit()
    

class PyGeneralLedgerTable(PyTableWithDate):
    completableEdit = subproxy('completableEdit', 'completable_edit', PyGUIObject)
    
    @signature('c@:i')
    def isAccountRow_(self, row_index):
        return self.py.is_account_row(self._getrow(row_index))
    
    @signature('c@:i')
    def isBoldRow_(self, row_index):
        return self.py.is_bold_row(self._getrow(row_index))

class FilterBarView(GUIObjectView):
    def disableTransfers(self): pass
    def enableTransfers(self): pass

class PyFilterBar(PyGUIObject2):
    def filterType(self) -> str:
        result = 'all'
        if self.model.filter_type is FilterType.Unassigned:
            result = 'unassigned'
        elif self.model.filter_type is FilterType.Income:
            result = 'income'
        elif self.model.filter_type is FilterType.Expense:
            result = 'expense'
        elif self.model.filter_type is FilterType.Transfer:
            result = 'transfer'
        elif self.model.filter_type is FilterType.Reconciled:
            result = 'reconciled'
        elif self.model.filter_type is FilterType.NotReconciled:
            result = 'not_reconciled'
        return result
    
    def setFilterType_(self, filter_type: str):
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
        self.model.filter_type = value
    
    #--- Python --> Cocoa    
    @dontwrap
    def disable_transfers(self):
        self.callback.disableTransfers()
    
    @dontwrap
    def enable_transfers(self):
        self.callback.enableTransfers()
    

class PyAccountPanel(PyPanel):
    
    typeList = subproxy('typeList', 'type_list', PySelectableList)
    currencyList = subproxy('currencyList', 'currency_list', PySelectableList)
    
    def name(self):
        return self.py.name
    
    def setName_(self, name):
        self.py.name = name
    
    def accountNumber(self):
        return self.py.account_number
    
    def setAccountNumber_(self, accountNumber):
        self.py.account_number = accountNumber
    
    def notes(self):
        return self.py.notes
    
    def setNotes_(self, notes):
        self.py.notes = notes
    
    @signature('c@:')
    def canChangeCurrency(self):
        return self.py.can_change_currency
    

class PySplitTable(PyTable2):
    def moveSplitFromRow_toRow_(self, from_row: int, to_row: int):
        self.model.move_split(from_row, to_row)
    

class PyPanelWithTransaction(PyPanel):
    completableEdit = subproxy('completableEdit', 'completable_edit', PyGUIObject)
    splitTable = subproxy('splitTable', 'split_table', PyGUIObject)
    
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

    def mctBalance(self):
        self.py.mct_balance()
    
    def date(self):
        return self.py.date
    
    def setDate_(self, value):
        self.py.date = value
    

class PyMassEditionPanel(PyPanel):
    completableEdit = subproxy('completableEdit', 'completable_edit', PyGUIObject)
    
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
    
    repeatTypeList = subproxy('repeatTypeList', 'repeat_type_list', PySelectableList)
    
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
    
    #--- Python -> Cocoa
    def refresh_repeat_every(self):
        self.cocoa.refreshRepeatEvery()
    
class PyBudgetPanel(PyPanel):
    
    repeatTypeList = subproxy('repeatTypeList', 'repeat_type_list', PySelectableList)
    accountList = subproxy('accountList', 'account_list', PySelectableList)
    targetList = subproxy('targetList', 'target_list', PySelectableList)
    
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
    
    def amount(self):
        return self.py.amount
    
    def setAmount_(self, value):
        self.py.amount = value
    
    def notes(self):
        return self.py.notes
    
    def setNotes_(self, value):
        self.py.notes = value
    
    #--- Python -> Cocoa
    def refresh_repeat_every(self):
        self.cocoa.refreshRepeatEvery()
    

class PyCustomDateRangePanel(PyPanel):
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
    accountList = subproxy('accountList', 'account_list', PySelectableList)

class PyExportPanel(PyPanel):
    accountTable = subproxy('accountTable', 'account_table', PyTable)
    
    @signature('c@:')
    def exportAll(self):
        return self.py.export_all
    
    @signature('v@:c')
    def setExportAll_(self, value):
        self.py.export_all = value
    
    def exportPath(self):
        return self.py.export_path
    
    def setExportPath_(self, value):
        self.py.export_path = value
    
    @signature('i@:')
    def exportFormat(self):
        return self.py.export_format
    
    @signature('v@:i')
    def setExportFormat_(self, value):
        self.py.export_format = value
    
    @signature('c@:')
    def currentDateRangeOnly(self):
        return self.py.current_daterange_only
    
    @signature('v@:c')
    def setCurrentDateRangeOnly_(self, value):
        self.py.current_daterange_only = value
    
    #--- Python --> Cocoa
    def set_table_enabled(self, enabled):
        self.cocoa.setTableEnabled_(enabled)
    
    def set_export_button_enabled(self, enabled):
        self.cocoa.setExportButtonEnabled_(enabled)
    

class PySearchField(PyGUIObject2):
    def query(self) -> str:
        return self.model.query
    
    def setQuery_(self, query: str):
        self.model.query = query
    

class DateRangeSelectorView(GUIObjectView):
    def animateBackward(self): pass
    def animateForward(self): pass
    def refreshCustomRanges(self): pass

class PyDateRangeSelector(PyGUIObject2):
    def selectPrevDateRange(self):
        self.model.select_prev_date_range()

    def selectMonthRange(self):
        self.model.select_month_range()

    def selectQuarterRange(self):
        self.model.select_quarter_range()

    def selectYearRange(self):
        self.model.select_year_range()
    
    def selectYearToDateRange(self):
        self.model.select_year_to_date_range()
    
    def selectNextDateRange(self):
        self.model.select_next_date_range()
    
    def selectTodayDateRange(self):
        self.model.select_today_date_range()
    
    def selectRunningYearRange(self):
        self.model.select_running_year_range()
    
    def selectAllTransactionsRange(self):
        self.model.select_all_transactions_range()
    
    def selectCustomDateRange(self):
        self.model.select_custom_date_range()
    
    def selectSavedRange_(self, slot: int):
        self.model.select_saved_range(slot)
    
    def display(self) -> str:
        return self.model.display
    
    def canNavigate(self) -> bool:
        return self.model.can_navigate
    
    def customRangeNames(self) -> list:
        return self.model.custom_range_names
    
    #--- Python -> Cocoa
    @dontwrap
    def animate_backward(self):
        self.callback.animateBackward()
    
    @dontwrap
    def animate_forward(self):
        self.callback.animateForward()
    
    @dontwrap
    def refresh_custom_ranges(self):
        self.callback.refreshCustomRanges()
    

class LookupView(GUIObjectView):
    def show(self): pass
    def hide(self): pass

class PyLookup(PyGUIObject2):
    def go(self):
        self.model.go()
    
    def names(self) -> list:
        return self.model.names
    
    def searchQuery(self) -> str:
        return self.model.search_query
    
    def setSearchQuery_(self, query: str):
        self.model.search_query = query
    
    def selectedIndex(self) -> int:
        return self.model.selected_index
    
    def setSelectedIndex_(self, index: int):
        self.model.selected_index = index
    
    #--- Python --> Cocoa
    @dontwrap
    def show(self):
        self.callback.show()
    
    @dontwrap
    def hide(self):
        self.callback.hide()
    

#--- Views
class PyBaseView(PyGUIContainer):
    # We can't use 'subproxy' here because it's too soon to have a reference to PyMainWindow. The
    # only PyMainWindow reference we can have is inside the method's code. copy/paste
    def mainwindow(self):
        if not hasattr(self, '_mainwindow'):
            self._mainwindow = PyMainWindow.alloc().initWithPy_(self.py.mainwindow)
            # Our proxy's 'cocoa' attr will always stay None because this proxy is not the main
            # proxy. We never bind the cocoa part.
        return self._mainwindow

class PyNetWorthView(PyBaseView):
    sheet = subproxy('sheet', 'bsheet', PyReport)
    nwgraph = subproxy('nwgraph', 'nwgraph', PyGraph)
    apie = subproxy('apie', 'apie', PyChart)
    lpie = subproxy('lpie', 'lpie', PyChart)
    
    #Python --> Cocoa
    def update_visibility(self):
        self.cocoa.updateVisibility()
    

class PyProfitView(PyBaseView):
    sheet = subproxy('sheet', 'istatement', PyReport)
    pgraph = subproxy('pgraph', 'pgraph', PyGraph)
    ipie = subproxy('ipie', 'ipie', PyChart)
    epie = subproxy('epie', 'epie', PyChart)
    
    #Python --> Cocoa
    def update_visibility(self):
        self.cocoa.updateVisibility()
    

class PyTransactionView(PyBaseView):
    filterBar = subproxy('filterBar', 'filter_bar', PyGUIObject)
    table = subproxy('table', 'ttable', PyTransactionTable)

class PyAccountView(PyBaseView):
    filterBar = subproxy('filterBar', 'filter_bar', PyGUIObject)
    table = subproxy('table', 'etable', PyEntryTable)
    balGraph = subproxy('balGraph', 'balgraph', PyGraph)
    barGraph = subproxy('barGraph', 'bargraph', PyGraph)
    
    @signature('c@:')
    def canToggleReconciliationMode(self):
        return self.py.can_toggle_reconciliation_mode
    
    @signature('c@:')
    def inReconciliationMode(self):
        return self.py.reconciliation_mode
    
    def toggleReconciliationMode(self):
        self.py.toggle_reconciliation_mode()
    
    #Python --> Cocoa
    def update_visibility(self):
        self.cocoa.updateVisibility()
    
    def refresh_reconciliation_button(self):
        self.cocoa.refreshReconciliationButton()
    
    def show_bar_graph(self):
        self.cocoa.showBarGraph()
    
    def show_line_graph(self):
        self.cocoa.showLineGraph()
    

class PyBudgetView(PyBaseView):
    table = subproxy('table', 'table', PyBudgetTable)

class PyScheduleView(PyBaseView):
    table = subproxy('table', 'table', PyScheduleTable)

class PyCashculatorView(PyBaseView):
    table = subproxy('table', 'atable', PyTable)
    
    def exportDB(self):
        self.py.export_db()
    
    def launchCC(self):
        self.py.launch_cc()
    
    def resetCCDB(self):
        self.py.reset_ccdb()
    

class PyGeneralLedgerView(PyBaseView):
    table = subproxy('table', 'gltable', PyGeneralLedgerTable)

class PyDocPropsView(PyBaseView):
    currencyList = subproxy('currencyList', 'currency_list', PySelectableList)
    firstWeekdayList = subproxy('firstWeekdayList', 'first_weekday_list', PySelectableList)
    aheadMonthsList = subproxy('aheadMonthsList', 'ahead_months_list', PySelectableList)
    yearStartMonthList = subproxy('yearStartMonthList', 'year_start_month_list', PySelectableList)

class PyEmptyView(PyBaseView):
    @signature('v@:i')
    def selectPaneType_(self, paneType):
        self.py.select_pane_type(paneType)

class PyMainWindow(PyGUIContainer):
    py_class = MainWindow
    
    searchField = subproxy('searchField', 'search_field', PyGUIObject)
    daterangeSelector = subproxy('daterangeSelector', 'daterange_selector', PyGUIObject)
    accountLookup = subproxy('accountLookup', 'account_lookup', PyGUIObject)
    completionLookup = subproxy('completionLookup', 'completion_lookup', PyGUIObject)
    
    accountPanel = subproxy('accountPanel', 'account_panel', PyAccountPanel)
    transactionPanel = subproxy('transactionPanel', 'transaction_panel', PyTransactionPanel)
    massEditPanel = subproxy('massEditPanel', 'mass_edit_panel', PyMassEditionPanel)
    budgetPanel = subproxy('budgetPanel', 'budget_panel', PyBudgetPanel)
    schedulePanel = subproxy('schedulePanel', 'schedule_panel', PySchedulePanel)
    customDateRangePanel = subproxy('customDateRangePanel', 'custom_daterange_panel', PyCustomDateRangePanel)
    accountReassignPanel = subproxy('accountReassignPanel', 'account_reassign_panel', PyAccountReassignPanel)
    exportPanel = subproxy('exportPanel', 'export_panel', PyExportPanel)
    
    nwview = subproxy('nwview', 'nwview', PyNetWorthView)
    pview = subproxy('pview', 'pview', PyProfitView)
    tview = subproxy('tview', 'tview', PyTransactionView)
    aview = subproxy('aview', 'aview', PyAccountView)
    scview = subproxy('scview', 'scview', PyScheduleView)
    bview = subproxy('bview', 'bview', PyBudgetView)
    ccview = subproxy('ccview', 'ccview', PyCashculatorView)
    glview = subproxy('glview', 'glview', PyGeneralLedgerView)
    dpview = subproxy('dpview', 'dpview', PyDocPropsView)
    emptyview = subproxy('emptyview', 'emptyview', PyEmptyView)
    
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
    
    @signature('v@:i')
    def toggleAreaVisibility_(self, area):
        self.py.toggle_area_visibility(area)
    
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
    def export(self):
        self.py.export()
    
    def statusLine(self):
        return self.py.status_line
    
    def hiddenAreas(self):
        return list(self.py.hidden_areas)
    
    #--- Column menu
    def columnMenuItems(self):
        return self.py.column_menu_items()
    
    @signature('v@:i')
    def toggleColumnMenuItemAtIndex_(self, index):
        self.py.toggle_column_menu_item(index)
    
    #--- Python -> Cocoa
    def change_current_pane(self):
        self.cocoa.changeSelectedPane()
    
    def refresh_panes(self):
        self.cocoa.refreshPanes()
    
    def refresh_undo_actions(self):
        self.cocoa.refreshUndoActions()
    
    def show_custom_date_range_panel(self):
        self.cocoa.showCustomDateRangePanel()
    
    def refresh_status_line(self):
        self.cocoa.refreshStatusLine()
    
    def show_message(self, message):
        self.cocoa.showMessage_(message)
    
    def update_area_visibility(self):
        self.cocoa.updateAreaVisibility()
    
    def view_closed(self, index):
        self.cocoa.viewClosedAtIndex_(index)
    

class PyImportTable(PyTable2):
    def bindRow_to_(self, source_index: int, dest_index: int):
        self.model.bind(source_index, dest_index)
    
    def canBindRow_to_(self, source_index: int, dest_index: int) -> bool:
        return self.model.can_bind(source_index, dest_index)
    
    def isTwoSided(self) -> bool:
        return self.model.is_two_sided
    
    def toggleImportStatus(self):
        self.model.toggle_import_status()
    
    def unbindRow_(self, index: int):
        self.model.unbind(index)
    
class ImportWindowView(GUIObjectView):
    def close(self): pass
    def closeSelectedTab(self): pass
    def refreshTabs(self): pass
    def refreshTargetAccounts(self): pass
    def show(self): pass
    def updateSelectedPane(self): pass

class PyImportWindow(PyListener2):
    def __init__(self, document: pyref):
        model = ImportWindow(None, document)
        PyListener2.__init__(self, model)
    
    def importTable(self) -> pyref:
        return self.model.import_table
    
    def accountCountAtIndex_(self, index: int) -> int:
        return self.model.panes[index].count
    
    def accountNameAtIndex_(self, index: int) -> str:
        return self.model.panes[index].name
    
    def canPerformSwap(self) -> bool:
        return self.model.can_perform_swap()
    
    def closePaneAtIndex_(self, index: int):
        self.model.close_pane(index)
    
    def importSelectedPane(self):
        self.model.import_selected_pane()
    
    def numberOfAccounts(self) -> int:
        return len(self.model.panes)
    
    def performSwap_(self, applyToAll: bool):
        self.model.perform_swap(apply_to_all=applyToAll)
    
    def selectedTargetAccountIndex(self) -> int:
        return self.model.selected_target_account_index
    
    def setSelectedTargetAccountIndex_(self, index: int):
        self.model.selected_target_account_index = index
    
    def setSelectedAccountIndex_(self, index: int):
        self.model.selected_pane_index = index
    
    def setSwapTypeIndex_(self, index: int):
        self.model.swap_type_index = index
    
    def targetAccountNames(self) -> list:
        return self.model.target_account_names
    
    #--- Python -> Cocoa
    @dontwrap
    def close(self):
        self.callback.close()
    
    @dontwrap
    def close_selected_tab(self):
        self.callback.closeSelectedTab()
    
    @dontwrap
    def refresh_tabs(self):
        self.callback.refreshTabs()
    
    @dontwrap
    def refresh_target_accounts(self):
        self.callback.refreshTargetAccounts()
    
    @dontwrap
    def show(self):
        self.callback.show()
    
    @dontwrap
    def update_selected_pane(self):
        self.callback.updateSelectedPane()
    

class CSVImportOptionsView(GUIObjectView):
    def refreshColumns(self): pass
    def refreshColumnsName(self): pass
    def refreshLayoutMenu(self): pass
    def refreshLines(self): pass
    def refreshTargets(self): pass
    def show(self): pass
    def hide(self): pass
    def showMessage_(self, msg: str): pass

class PyCSVImportOptions(PyListener2):
    def __init__(self, document: pyref):
        model = CSVOptions(None, document)
        PyListener2.__init__(self, model)
    
    def columnNameAtIndex_(self, index: int) -> str:
        return self.model.get_column_name(index)
    
    def continueImport(self):
        self.model.continue_import()
    
    def deleteSelectedLayout(self):
        self.model.delete_selected_layout()
    
    def fieldSeparator(self) -> str:
        return self.model.field_separator
    
    def layoutNames(self) -> list:
        return self.model.layout_names
    
    def lineIsImported_(self, index: int) -> bool:
        return not self.model.line_is_excluded(index)
    
    def numberOfColumns(self) -> int:
        return len(self.model.columns)
    
    def numberOfLines(self) -> int:
        return len(self.model.lines)
    
    def newLayout_(self, name: str):
        self.model.new_layout(name)
    
    def renameSelectedLayout_(self, newname: str):
        self.model.rename_selected_layout(newname)
    
    def rescan(self):
        self.model.rescan()
    
    def selectedLayoutName(self) -> str:
        return self.model.layout.name
    
    def selectedTargetIndex(self) -> int:
        return self.model.selected_target_index
    
    def selectLayout_(self, name: str):
        self.model.select_layout(name)
    
    def setColumn_fieldForTag_(self, index: int, tag: int):
        field = CSV_FIELD_ORDER[tag]
        self.model.set_column_field(index, field)
    
    def setEncodingIndex_(self, index: int):
        self.model.encoding_index = index
    
    def setFieldSeparator_(self, fieldSep: str):
        self.model.field_separator = fieldSep
    
    def setSelectedTargetIndex_(self, index: int):
        self.model.selected_target_index = index
    
    def supportedEncodings(self) -> list:
        return CSV_SUPPORTED_ENCODINGS
    
    def targetAccountNames(self) -> list:
        return self.model.target_account_names
    
    def toggleLineExclusion_(self, index: int):
        self.model.set_line_excluded(index, not self.model.line_is_excluded(index))
    
    def valueForRow_column_(self, row: int, column: int) -> str:
        return self.model.lines[row][column]
    
    #--- Python -> Cocoa
    @dontwrap
    def refresh_columns(self):
        self.callback.refreshColumns()
    
    @dontwrap
    def refresh_columns_name(self):
        self.callback.refreshColumnsName()
    
    @dontwrap
    def refresh_layout_menu(self):
        self.callback.refreshLayoutMenu()
    
    @dontwrap
    def refresh_lines(self):
        self.callback.refreshLines()
    
    @dontwrap
    def refresh_targets(self):
        self.callback.refreshTargets()
    
    @dontwrap
    def show(self):
        self.callback.show()
    
    @dontwrap
    def hide(self):
        self.callback.hide()
    
    @dontwrap
    def show_message(self, msg):
        self.callback.showMessage_(msg)
    

class PyDateWidget:
    def __init__(self):
        NSDateFormatter.setDefaultFormatterBehavior_(NSDateFormatterBehavior10_4)
        f = NSDateFormatter.alloc().init()
        f.setDateStyle_(NSDateFormatterShortStyle)
        f.setTimeStyle_(NSDateFormatterNoStyle)
        self.date_format = clean_format(f.dateFormat())
        self.w = DateWidget(self.date_format)
    
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
    
    def type_(self, something: str):
        self.w.type(something)
    
    def setDate_(self, str_date: str):
        self.w.text = str_date
    
    def text(self) -> str:
        return self.w.text
    
    def selection(self) -> list: # list of numbers
        return self.w.selection
    

class PyCompletableEdit(PyGUIObject2):
    def setAttrname_(self, attrname: str):
        self.model.attrname = attrname
    
    def text(self) -> str:
        return self.model.text
    
    def setText_(self, value: str):
        self.model.text = value
    
    def completion(self) -> str:
        return self.model.completion
    
    def commit(self):
        self.model.commit()
    
    def down(self):
        self.model.down()
    
    def up(self):
        self.model.up()
    
    def lookup(self):
        self.model.lookup()
    

#--- Printing

class PyPrintView:
    py_class = PrintView
    
    # The parent of the PyPrintView is a View object
    def __init__(self, parent: pyref):
        self.model = self.py_class(parent)
    
    def title(self) -> str:
        return self.model.title
    

class PySplitPrint(PyPrintView):
    def splitCountAtRow_(self, row: int) -> int:
        return self.model.split_count_at_row(row)
    
    def splitValuesAtRow_splitRow_(self, row: int, split_row: int) -> list:
        return self.model.split_values(row, split_row)

class PyTransactionPrint(PySplitPrint):
    py_class = TransactionPrint

class PyEntryPrint(PySplitPrint):
    py_class = EntryPrint
