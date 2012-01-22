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
from cocoa.inter2 import (PyGUIObject2, GUIObjectView, PyTable2, PyColumns2, PyOutline2, OutlineView,
    PySelectableList2)
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
    

class PyTableWithDate(PyTable2):
    def isEditedRowInTheFuture(self) -> bool:
        if self.model.edited is None:
            return False
        return self.model.edited.is_date_in_future()
    
    def isEditedRowInThePast(self) -> bool:
        if self.model.edited is None:
            return False
        return self.model.edited.is_date_in_past()
    

class PyChart(PyListener2):
    def data(self) -> list:
        return self.model.data
    
    def title(self) -> str:
        return self.model.title
    
    def currency(self) -> str:
        return self.model.currency.code
    

class PyGraph(PyChart):
    def xMin(self) -> float:
        return self.model.xmin

    def xMax(self) -> float:
        return self.model.xmax
    
    def yMin(self) -> float:
        return self.model.ymin
    
    def yMax(self) -> float:
        return self.model.ymax
    
    def xToday(self) -> float:
        return getattr(self.model, 'xtoday', 0) # bar charts don't have a xtoday attr
    
    def xLabels(self) -> list:
        return self.model.xlabels
    
    def xTickMarks(self) -> list:
        return self.model.xtickmarks
    
    def yLabels(self) -> list:
        return self.model.ylabels
    
    def yTickMarks(self) -> list:
        return self.model.ytickmarks
    

class ReportView(OutlineView):
    def refreshExpandedPaths(self): pass

class PyReport(PyOutline2):
    def columns(self) -> pyref:
        return self.model.columns
    
    def canDeleteSelected(self) -> bool:
        return self.model.can_delete()
    
    def deleteSelected(self):
        self.model.delete()
    
    def canMovePaths_toPath_(self, source_paths: list, dest_path: list) -> bool:
        return self.model.can_move(source_paths, dest_path)
    
    def movePaths_toPath_(self, source_paths: list, dest_path: list):
        self.model.move(source_paths, dest_path)
    
    def showSelectedAccount(self):
        self.model.show_selected_account()
    
    def canShowSelectedAccount(self) -> bool:
        return self.model.can_show_selected_account
    
    def toggleExcluded(self):
        self.model.toggle_excluded()
    
    def expandPath_(self, path: list):
        self.model.expand_node(self.model.get_node(path))
        
    def collapsePath_(self, path: list):
        self.model.collapse_node(self.model.get_node(path))
    
    def expandedPaths(self) -> list:
        return self.model.expanded_paths
    
    def selectionAsCSV(self) -> str:
        return self.model.selection_as_csv()
    
    # Python --> Cocoa
    @dontwrap
    def refresh_expanded_paths(self):
        self.callback.refreshExpandedPaths()
    

class PanelView(GUIObjectView):
    def preLoad(self): pass
    def postLoad(self): pass
    def preSave(self): pass

class PyPanel(PyGUIObject2):
    def savePanel(self):
        self.model.save()
    
    # Python --> Cocoa
    @dontwrap
    def pre_load(self):
        self.callback.preLoad()
    
    @dontwrap
    def post_load(self):
        self.callback.postLoad()
    
    @dontwrap
    def pre_save(self):
        self.callback.preSave()
    

#--- GUI layer classes

class PyEntryTable(PyTableWithDate):
    def completableEdit(self) -> pyref:
        return self.model.completable_edit
    
    def canMoveRows_to_(self, rows: list, position: int) -> bool:
        return self.model.can_move(rows, position)

    def canReconcileEntryAtRow_(self, row: int) -> bool:
        return self.model[row].can_reconcile()
    
    def isBalanceNegativeAtRow_(self, row: int) -> bool:
        return self.model[row].is_balance_negative()
    
    def isBoldAtRow_(self, row: int) -> bool:
        return self.model[row].is_bold
    
    def moveRows_to_(self, rows: list, position: int):
        self.model.move(rows, position)

    def showTransferAccount(self):
        self.model.show_transfer_account()
    
    def toggleReconciled(self):
        self.model.toggle_reconciled()
    
    def toggleReconciledAtRow_(self, row_index: int):
        self.model[row_index].toggle_reconciled()
    

class PyTransactionTable(PyTableWithDate):
    def completableEdit(self) -> pyref:
        return self.model.completable_edit
    
    def isBoldAtRow_(self, row: int) -> bool:
        return self.model[row].is_bold
    
    def canMoveRows_to_(self, rows: list, position: int) -> bool:
        return self.model.can_move(rows, position)
    
    def moveRows_to_(self, rows: list, position: int):
        self.model.move(rows, position)
    
    def showFromAccount(self):
        self.model.show_from_account()
    
    def showToAccount(self):
        self.model.show_to_account()
    

class PyScheduleTable(PyTable2):
    def editItem(self):
        self.model.edit()
    

class PyBudgetTable(PyTable2):
    def editItem(self):
        self.model.edit()
    

class PyGeneralLedgerTable(PyTableWithDate):
    def completableEdit(self) -> pyref:
        return self.model.completable_edit
    
    def isAccountRow_(self, row_index: int) -> bool:
        return self.model.is_account_row(self._getrow(row_index))
    
    def isBoldRow_(self, row_index: int) -> bool:
        return self.model.is_bold_row(self._getrow(row_index))
    

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
    def typeList(self) -> pyref:
        return self.model.type_list
    
    def currencyList(self) -> pyref:
        return self.model.currency_list
    
    def name(self) -> str:
        return self.model.name
    
    def setName_(self, name: str):
        self.model.name = name
    
    def accountNumber(self) -> str:
        return self.model.account_number
    
    def setAccountNumber_(self, accountNumber: str):
        self.model.account_number = accountNumber
    
    def notes(self) -> str:
        return self.model.notes
    
    def setNotes_(self, notes: str):
        self.model.notes = notes
    
    def canChangeCurrency(self) -> bool:
        return self.model.can_change_currency
    

class PySplitTable(PyTable2):
    def moveSplitFromRow_toRow_(self, from_row: int, to_row: int):
        self.model.move_split(from_row, to_row)
    

class PanelWithTransactionView(PanelView):
    def refreshForMultiCurrency(self): pass

class PyPanelWithTransaction(PyPanel):
    def completableEdit(self) -> pyref:
        return self.model.completable_edit
    
    def splitTable(self) -> pyref:
        return self.model.split_table
    
    def description(self) -> str:
        return self.model.description
    
    def setDescription_(self, value: str):
        self.model.description = value
    
    def payee(self) -> str:
        return self.model.payee
    
    def setPayee_(self, value: str):
        self.model.payee = value
    
    def checkno(self) -> str:
        return self.model.checkno
    
    def setCheckno_(self, value: str):
        self.model.checkno = value
    
    def notes(self) -> str:
        return self.model.notes
    
    def setNotes_(self, value: str):
        self.model.notes = value
    
    def isMultiCurrency(self) -> bool:
        return self.model.is_multi_currency
    
    #--- Python -> Cocoa
    @dontwrap
    def refresh_for_multi_currency(self):
        self.callback.refreshForMultiCurrency()
    

class PyTransactionPanel(PyPanelWithTransaction):
    def mctBalance(self):
        self.model.mct_balance()
    
    def date(self) -> str:
        return self.model.date
    
    def setDate_(self, value: str):
        self.model.date = value
    

class PyMassEditionPanel(PyPanel):
    def completableEdit(self) -> pyref:
        return self.model.completable_edit
    
    def availableCurrencies(self) -> list:
        return ['%s - %s' % (currency.code, currency.name) for currency in Currency.all]
    
    def canChangeAccounts(self) -> bool:
        return self.model.can_change_accounts
    
    def canChangeAmount(self) -> bool:
        return self.model.can_change_amount
    
    def dateEnabled(self) -> bool:
        return self.model.date_enabled
    
    def setDateEnabled_(self, value: bool):
        self.model.date_enabled = value
    
    def descriptionEnabled(self) -> bool:
        return self.model.description_enabled
    
    def setDescriptionEnabled_(self, value: bool):
        self.model.description_enabled = value
    
    def payeeEnabled(self) -> bool:
        return self.model.payee_enabled
    
    def setPayeeEnabled_(self, value: bool):
        self.model.payee_enabled = value
    
    def checknoEnabled(self) -> bool:
        return self.model.checkno_enabled
    
    def setChecknoEnabled_(self, value: bool):
        self.model.checkno_enabled = value
    
    def fromEnabled(self) -> bool:
        return self.model.from_enabled
    
    def setFromEnabled_(self, value: bool):
        self.model.from_enabled = value
    
    def toEnabled(self) -> bool:
        return self.model.to_enabled
    
    def setToEnabled_(self, value: bool):
        self.model.to_enabled = value
    
    def amountEnabled(self) -> bool:
        return self.model.amount_enabled
    
    def setAmountEnabled_(self, value: bool):
        self.model.amount_enabled = value
    
    def currencyEnabled(self) -> bool:
        return self.model.currency_enabled
    
    def setCurrencyEnabled_(self, value: bool):
        self.model.currency_enabled = value
    
    def date(self) -> str:
        return self.model.date
    
    def setDate_(self, value: str):
        self.model.date = value
    
    def description(self) -> str:
        return self.model.description
    
    def setDescription_(self, value: str):
        self.model.description = value
    
    def payee(self) -> str:
        return self.model.payee
    
    def setPayee_(self, value: str):
        self.model.payee = value
    
    def checkno(self) -> str:
        return self.model.checkno
    
    def setCheckno_(self, value: str):
        self.model.checkno = value
    
    def fromAccount(self) -> str: # We cannot use the underscore to escape the kw. It messes with pyobjc
        return self.model.from_
    
    def setFromAccount_(self, value: str):
        self.model.from_ = value
    
    def to(self) -> str:
        return self.model.to
    
    def setTo_(self, value: str):
        self.model.to = value
    
    def amount(self) -> str:
        return self.model.amount
    
    def setAmount_(self, value: str):
        self.model.amount = value
    
    def currencyIndex(self) -> int:
        return self.model.currency_index
    
    def setCurrencyIndex_(self, value: int):
        self.model.currency_index = value
    

class SchedulePanelView(PanelWithTransactionView):
    def refreshRepeatEvery(self): pass

class PySchedulePanel(PyPanelWithTransaction):
    def repeatTypeList(self) -> pyref:
        return self.model.repeat_type_list
    
    def startDate(self) -> str:
        return self.model.start_date
    
    def setStartDate_(self, value: str):
        self.model.start_date = value
    
    def stopDate(self) -> str:
        return self.model.stop_date
    
    def setStopDate_(self, value: str):
        self.model.stop_date = value
    
    def repeatEvery(self) -> int:
        return self.model.repeat_every
    
    def setRepeatEvery_(self, value: int):
        self.model.repeat_every = value
    
    def repeatEveryDesc(self) -> str:
        return self.model.repeat_every_desc
    
    #--- Python -> Cocoa
    @dontwrap
    def refresh_repeat_every(self):
        self.callback.refreshRepeatEvery()
    
class BudgetPanelView(PanelView):
    def refreshRepeatEvery(self): pass

class PyBudgetPanel(PyPanel):
    def repeatTypeList(self) -> pyref:
        return self.model.repeat_type_list
    
    def accountList(self) -> pyref:
        return self.model.account_list
    
    def targetList(self) -> pyref:
        return self.model.target_list
    
    def startDate(self) -> str:
        return self.model.start_date
    
    def setStartDate_(self, value: str):
        self.model.start_date = value
    
    def stopDate(self) -> str:
        return self.model.stop_date
    
    def setStopDate_(self, value: str):
        self.model.stop_date = value
    
    def repeatEvery(self) -> int:
        return self.model.repeat_every
    
    def setRepeatEvery_(self, value: int):
        self.model.repeat_every = value
    
    def repeatEveryDesc(self) -> str:
        return self.model.repeat_every_desc
    
    def amount(self) -> str:
        return self.model.amount
    
    def setAmount_(self, value: str):
        self.model.amount = value
    
    def notes(self) -> str:
        return self.model.notes
    
    def setNotes_(self, value: str):
        self.model.notes = value
    
    #--- Python -> Cocoa
    @dontwrap
    def refresh_repeat_every(self):
        self.callback.refreshRepeatEvery()
    

class PyCustomDateRangePanel(PyPanel):
    def startDate(self) -> str:
        return self.model.start_date
    
    def setStartDate_(self, value: str):
        self.model.start_date = value
    
    def endDate(self) -> str:
        return self.model.end_date
    
    def setEndDate_(self, value: str):
        self.model.end_date = value
    
    def slotIndex(self) -> int:
        return self.model.slot_index
    
    def setSlotIndex_(self, index: int):
        self.model.slot_index = index
    
    def slotName(self) -> str:
        return self.model.slot_name
    
    def setSlotName_(self, name: str):
        self.model.slot_name = name
    

class PyAccountReassignPanel(PyPanel):
    def accountList(self) -> pyref:
        return self.model.account_list
    
class ExportPanelView(PanelView):
    def setTableEnabled_(self, enabled: bool): pass
    def setExportButtonEnabled_(self, enabled: bool): pass

class PyExportPanel(PyPanel):
    def accountTable(self) -> pyref:
        return self.model.account_table
    
    def exportAll(self) -> bool:
        return self.model.export_all
    
    def setExportAll_(self, value: bool):
        self.model.export_all = value
    
    def exportPath(self) -> str:
        return self.model.export_path
    
    def setExportPath_(self, value: str):
        self.model.export_path = value
    
    def exportFormat(self) -> int:
        return self.model.export_format
    
    def setExportFormat_(self, value: int):
        self.model.export_format = value
    
    def currentDateRangeOnly(self) -> bool:
        return self.model.current_daterange_only
    
    def setCurrentDateRangeOnly_(self, value: bool):
        self.model.current_daterange_only = value
    
    #--- Python --> Cocoa
    @dontwrap
    def set_table_enabled(self, enabled):
        self.callback.setTableEnabled_(enabled)
    
    @dontwrap
    def set_export_button_enabled(self, enabled):
        self.callback.setExportButtonEnabled_(enabled)
    

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

class PyBaseView2(PyListener2):
    def mainwindow(self) -> pyref:
        return self.model.mainwindow
    
    def hiddenAreas(self) -> list:
        return list(self.model.mainwindow.hidden_areas)
    

class ViewWithGraphView:
    def updateVisibility(self): pass

class PyNetWorthView(PyBaseView2):
    def sheet(self) -> pyref:
        return self.model.bsheet
    
    def nwgraph(self) -> pyref:
        return self.model.nwgraph
    
    def apie(self) -> pyref:
        return self.model.apie
    
    def lpie(self) -> pyref:
        return self.model.lpie
    
    #Python --> Cocoa
    @dontwrap
    def update_visibility(self):
        self.callback.updateVisibility()
    

class PyProfitView(PyBaseView2):
    def sheet(self) -> pyref:
        return self.model.istatement
    
    def pgraph(self) -> pyref:
        return self.model.pgraph
    
    def ipie(self) -> pyref:
        return self.model.ipie
    
    def epie(self) -> pyref:
        return self.model.epie
    
    #Python --> Cocoa
    @dontwrap
    def update_visibility(self):
        self.callback.updateVisibility()
    

class PyTransactionView(PyBaseView2):
    def filterBar(self) -> pyref:
        return self.model.filter_bar
    
    def table(self) -> pyref:
        return self.model.ttable
    

class AccountViewView(ViewWithGraphView):
    def refreshReconciliationButton(self): pass
    def showBarGraph(self): pass
    def showLineGraph(self): pass

class PyAccountView(PyBaseView2):
    def filterBar(self) -> pyref:
        return self.model.filter_bar
    
    def table(self) -> pyref:
        return self.model.etable
    
    def balGraph(self) -> pyref:
        return self.model.balgraph
    
    def barGraph(self) -> pyref:
        return self.model.bargraph
    
    def canToggleReconciliationMode(self) -> bool:
        return self.model.can_toggle_reconciliation_mode
    
    def inReconciliationMode(self) -> bool:
        return self.model.reconciliation_mode
    
    def toggleReconciliationMode(self):
        self.model.toggle_reconciliation_mode()
    
    #Python --> Cocoa
    @dontwrap
    def update_visibility(self):
        self.callback.updateVisibility()
    
    @dontwrap
    def refresh_reconciliation_button(self):
        self.callback.refreshReconciliationButton()
    
    @dontwrap
    def show_bar_graph(self):
        self.callback.showBarGraph()
    
    @dontwrap
    def show_line_graph(self):
        self.callback.showLineGraph()
    

class PyBudgetView(PyBaseView2):
    def table(self) -> pyref:
        return self.model.table
    

class PyScheduleView(PyBaseView2):
    def table(self) -> pyref:
        return self.model.table
    

class PyCashculatorView(PyBaseView2):
    def table(self) -> pyref:
        return self.model.atable
    
    def exportDB(self):
        self.model.export_db()
    
    def launchCC(self):
        self.model.launch_cc()
    
    def resetCCDB(self):
        self.model.reset_ccdb()
    

class PyGeneralLedgerView(PyBaseView2):
    def table(self) -> pyref:
        return self.model.gltable
    

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
    
    accountPanel = subproxy('accountPanel', 'account_panel', PyGUIObject)
    transactionPanel = subproxy('transactionPanel', 'transaction_panel', PyGUIObject)
    massEditPanel = subproxy('massEditPanel', 'mass_edit_panel', PyGUIObject)
    budgetPanel = subproxy('budgetPanel', 'budget_panel', PyGUIObject)
    schedulePanel = subproxy('schedulePanel', 'schedule_panel', PyGUIObject)
    customDateRangePanel = subproxy('customDateRangePanel', 'custom_daterange_panel', PyGUIObject)
    accountReassignPanel = subproxy('accountReassignPanel', 'account_reassign_panel', PyGUIObject)
    exportPanel = subproxy('exportPanel', 'export_panel', PyGUIObject)
    
    nwview = subproxy('nwview', 'nwview', PyGUIObject)
    pview = subproxy('pview', 'pview', PyGUIObject)
    tview = subproxy('tview', 'tview', PyGUIObject)
    aview = subproxy('aview', 'aview', PyGUIObject)
    scview = subproxy('scview', 'scview', PyGUIObject)
    bview = subproxy('bview', 'bview', PyGUIObject)
    ccview = subproxy('ccview', 'ccview', PyGUIObject)
    glview = subproxy('glview', 'glview', PyGUIObject)
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
