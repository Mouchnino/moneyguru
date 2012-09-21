# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import os.path as op
from objp.util import pyref, dontwrap, nsrect, nssize, nspoint

from cocoa import install_exception_hook, proxy, install_cocoa_logger
from cocoa.inter import (PyGUIObject, GUIObjectView, PyTextField, PyTable, PyColumns, PyOutline,
    OutlineView, PySelectableList, PyFairware)
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

# Force to collect modules normally missing by the dependencies collector.
import xml.etree.ElementTree

class PyMoneyGuruApp(PyFairware):
    def __init__(self):
        LOGGING_LEVEL = logging.DEBUG if proxy.prefValue_('DebugMode') else logging.WARNING
        logging.basicConfig(level=LOGGING_LEVEL, format='%(levelname)s %(message)s')
        install_exception_hook()
        install_cocoa_logger()
        logging.debug('started in debug mode')
        std_caches_path = Path(proxy.getCachePath())
        cache_path = std_caches_path + 'moneyGuru'
        appdata_path = op.join(proxy.getAppdataPath(), 'moneyGuru')
        plugin_model_path = op.join(proxy.getResourcePath(), 'plugin_examples')
        currency_code = nonone(proxy.systemCurrency(), 'USD')
        logging.info('Currency code: {0}'.format(currency_code))
        try:
            system_currency = Currency(currency_code)
        except ValueError: # currency does not exist
            logging.warning('System currency {0} is not supported. Falling back to USD.'.format(currency_code))
            system_currency = USD
        date_format = proxy.systemShortDateFormat()
        logging.info('System date format: %s' % date_format)
        date_format = clean_format(date_format)
        logging.info('Cleaned date format: %s' % date_format)
        decimal_sep = proxy.systemNumberDecimalSeparator()
        grouping_sep = proxy.systemNumberGroupingSeparator()
        logging.info('System numeric separators: %s and %s' % (grouping_sep, decimal_sep))
        model = Application(self, date_format=date_format, decimal_sep=decimal_sep, 
            grouping_sep=grouping_sep, default_currency=system_currency, cache_path=cache_path,
            appdata_path=appdata_path, plugin_model_path=plugin_model_path)
        PyFairware.__init__(self, model)
    
    #--- Public
    def isFirstRun(self) -> bool:
        return self.model.is_first_run
    
    def openPluginFolder(self):
        self.model.open_plugin_folder()
    
    def shutdown(self):
        self.model.shutdown()
    
    #--- Preferences
    def autoSaveInterval(self) -> int:
        return self.model.autosave_interval
    
    def setAutoSaveInterval_(self, minutes: int):
        self.model.autosave_interval = minutes
    
    def autoDecimalPlace(self) -> bool:
        return self.model.auto_decimal_place
    
    def setAutoDecimalPlace_(self, value: bool):
        self.model.auto_decimal_place = value
    
    #--- model --> view
    @dontwrap
    def reveal_path(self, path):
        proxy.revealPath_(str(path))
    

class DocumentView(GUIObjectView):
    def queryForScheduleScope(self) -> int: pass

class PyDocument(PyGUIObject):
    def __init__(self, app: pyref):
        model = Document(app.model)
        PyGUIObject.__init__(self, model)
        self.model.connect()
    
    #--- Undo
    def canUndo(self) -> bool:
        return self.model.can_undo()
    
    def undoDescription(self) -> str:
        return self.model.undo_description()
    
    def undo(self):
        self.model.undo()
    
    def canRedo(self) -> bool:
        return self.model.can_redo()
    
    def redoDescription(self) -> str:
        return self.model.redo_description()
    
    def redo(self):
        self.model.redo()
    
    #--- Misc
    def adjustExampleFile(self):
        self.model.adjust_example_file()
    
    def loadFromFile_(self, filename: str) -> str:
        try:
            self.model.load_from_xml(filename)
        except FileFormatError as e:
            return str(e)
    
    def saveToFile_(self, filename: str):
        self.model.save_to_xml(filename)
    
    def import_(self, filename: str) -> str:
        try:
            self.model.parse_file_for_import(filename)
        except FileFormatError as e:
            return str(e)
    
    def isDirty(self) -> bool:
        return self.model.is_dirty()
    
    def stopEdition(self):
        self.model.stop_edition()
    
    def close(self):
        self.model.close()
        self.model.disconnect()
    
    #--- Python -> Cocoa
    @dontwrap
    def query_for_schedule_scope(self):
        return self.callback.queryForScheduleScope()
    

#--- Root classes
class PyTableWithDate(PyTable):
    def isEditedRowInTheFuture(self) -> bool:
        if self.model.edited is None:
            return False
        return self.model.edited.is_date_in_future()
    
    def isEditedRowInThePast(self) -> bool:
        if self.model.edited is None:
            return False
        return self.model.edited.is_date_in_past()
    

class ChartView(GUIObjectView):
    def drawLineFrom_to_penID_(self, p1: nspoint, p2: nspoint, pen_id: int): pass
    def drawRect_penID_brushID_(self, rect: nsrect, pen_id: int, brush_id: int): pass
    def drawPieWithCenter_radius_startAngle_spanAngle_brushID_(self, center: nspoint, radius: float, start_angle: float, span_angle: float, brush_id: int): pass
    def drawPolygonWithPoints_penID_brushID_(self, points: list, pen_id: int, brush_id: int): pass
    def drawText_inRect_withFontID_(self, text: str, rect: nsrect, font_id: int): pass
    def sizeForText_withFontID_(self, text: str, font_id: int) -> nssize: pass

class PyChart(PyGUIObject):
    def data(self) -> list:
        return self.model.data
    
    def title(self) -> str:
        return self.model.title
    
    def currency(self) -> str:
        return self.model.currency.code
    
    def setViewWidth_height_(self, width: int, height: int):
        self.model.set_view_size(width, height)
    
    def draw(self):
        self.model.draw()
    
    #--- Python -> Cocoa
    @dontwrap
    def draw_line(self, p1, p2, pen_id):
        self.callback.drawLineFrom_to_penID_(p1, p2, pen_id)
    
    @dontwrap
    def draw_rect(self, rect, pen_id, brush_id):
        self.callback.drawRect_penID_brushID_(rect, nonone(pen_id, -1), nonone(brush_id, -1))
    
    @dontwrap
    def draw_pie(self, center, radius, start_angle, span_angle, brush_id):
        self.callback.drawPieWithCenter_radius_startAngle_spanAngle_brushID_(center, radius, start_angle, span_angle, brush_id)
    
    @dontwrap
    def draw_polygon(self, points, pen_id, brush_id):
        points = [list(p) for p in points]
        self.callback.drawPolygonWithPoints_penID_brushID_(points, nonone(pen_id, -1), nonone(brush_id, -1))
    
    @dontwrap
    def draw_text(self, text, rect, font_id):
        self.callback.drawText_inRect_withFontID_(text, rect, font_id)
    
    @dontwrap
    def text_size(self, text, font_id):
        return self.callback.sizeForText_withFontID_(text, font_id)
    

class PyGraph(PyChart):
    def drawWithXFactor_yFactor_(self, xFactor: float, yFactor: float):
        self.model.draw(xFactor, yFactor)
    
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

class PyReport(PyOutline):
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

class PyPanel(PyGUIObject):
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
    

class PyScheduleTable(PyTable):
    def editItem(self):
        self.model.edit()
    

class PyBudgetTable(PyTable):
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

class PyFilterBar(PyGUIObject):
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
    

class PySplitTable(PyTable):
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
    def dateField(self) -> pyref:
        return self.model.date_field
    
    def descriptionField(self) -> pyref:
        return self.model.description_field
    
    def payeeField(self) -> pyref:
        return self.model.payee_field
    
    def checknoField(self) -> pyref:
        return self.model.checkno_field
    
    def fromField(self) -> pyref:
        return self.model.from_field
    
    def toField(self) -> pyref:
        return self.model.to_field
    
    def amountField(self) -> pyref:
        return self.model.amount_field
    
    def completableEdit(self) -> pyref:
        return self.model.completable_edit
    
    def currencyList(self) -> pyref:
        return self.model.currency_list
    
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
    

class DateRangeSelectorView(GUIObjectView):
    def animateBackward(self): pass
    def animateForward(self): pass
    def refreshCustomRanges(self): pass

class PyDateRangeSelector(PyGUIObject):
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

class PyLookup(PyGUIObject):
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
class PyBaseView(PyGUIObject):
    def mainwindow(self) -> pyref:
        return self.model.mainwindow
    
    def hiddenAreas(self) -> list:
        return list(self.model.mainwindow.hidden_areas)
    

class ViewWithGraphView:
    def updateVisibility(self): pass

class PyNetWorthView(PyBaseView):
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
    

class PyProfitView(PyBaseView):
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
    

class PyTransactionView(PyBaseView):
    def filterBar(self) -> pyref:
        return self.model.filter_bar
    
    def table(self) -> pyref:
        return self.model.ttable
    

class AccountViewView(ViewWithGraphView):
    def refreshReconciliationButton(self): pass
    def showBarGraph(self): pass
    def showLineGraph(self): pass

class PyAccountView(PyBaseView):
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
    

class PyBudgetView(PyBaseView):
    def table(self) -> pyref:
        return self.model.table
    

class PyScheduleView(PyBaseView):
    def table(self) -> pyref:
        return self.model.table
    

class PyCashculatorView(PyBaseView):
    def table(self) -> pyref:
        return self.model.atable
    
    def exportDB(self):
        self.model.export_db()
    
    def launchCC(self):
        self.model.launch_cc()
    
    def resetCCDB(self):
        self.model.reset_ccdb()
    

class PyGeneralLedgerView(PyBaseView):
    def table(self) -> pyref:
        return self.model.gltable
    

class PyDocPropsView(PyBaseView):
    def currencyList(self) -> pyref:
        return self.model.currency_list
    
    def firstWeekdayList(self) -> pyref:
        return self.model.first_weekday_list
    
    def aheadMonthsList(self) -> pyref:
        return self.model.ahead_months_list
    
    def yearStartMonthList(self) -> pyref:
        return self.model.year_start_month_list
    

class PyEmptyView(PyBaseView):
    def pluginList(self) -> pyref:
        return self.model.plugin_list
    
    def selectPaneType_(self, paneType: int):
        self.model.select_pane_type(paneType)
    
    def openSelectedPlugin(self):
        self.model.open_selected_plugin()
    

class PyReadOnlyPluginView(PyBaseView):
    def table(self) -> pyref:
        return self.model.table
    

class MainWindowView(GUIObjectView):
    def changeSelectedPane(self): pass
    def refreshPanes(self): pass
    def refreshUndoActions(self): pass
    def showCustomDateRangePanel(self): pass
    def refreshStatusLine(self): pass
    def showMessage_(self, message: str): pass
    def updateAreaVisibility(self): pass
    def viewClosedAtIndex_(self, index: int): pass

class PyMainWindow(PyGUIObject):
    def __init__(self, document: pyref):
        model = MainWindow(document.model)
        PyGUIObject.__init__(self, model)
    
    def bindCallback_(self, callback: pyref):
        PyGUIObject.bindCallback_(self, callback)
        self.model.connect()
    
    def searchField(self) -> pyref:
        return self.model.search_field
    
    def daterangeSelector(self) -> pyref:
        return self.model.daterange_selector
    
    def accountLookup(self) -> pyref:
        return self.model.account_lookup
    
    def completionLookup(self) -> pyref:
        return self.model.completion_lookup
    
    def accountPanel(self) -> pyref:
        return self.model.account_panel
    
    def transactionPanel(self) -> pyref:
        return self.model.transaction_panel
    
    def massEditPanel(self) -> pyref:
        return self.model.mass_edit_panel
    
    def budgetPanel(self) -> pyref:
        return self.model.budget_panel
    
    def schedulePanel(self) -> pyref:
        return self.model.schedule_panel
    
    def customDateRangePanel(self) -> pyref:
        return self.model.custom_daterange_panel
    
    def accountReassignPanel(self) -> pyref:
        return self.model.account_reassign_panel
    
    def exportPanel(self) -> pyref:
        return self.model.export_panel
    
    def selectNextView(self):
        self.model.select_next_view()
    
    def selectPreviousView(self):
        self.model.select_previous_view()
    
    def currentPaneIndex(self) -> int:
        return self.model.current_pane_index
    
    def setCurrentPaneIndex_(self, index: int):
        self.model.current_pane_index = index
    
    def paneCount(self) -> int:
        return self.model.pane_count
    
    def paneLabelAtIndex_(self, index: int) -> str:
        return self.model.pane_label(index)
    
    def paneTypeAtIndex_(self, index: int) -> int:
        return self.model.pane_type(index)
    
    def paneViewRefAtIndex_(self, index: int) -> pyref:
        return self.model.pane_view(index)
    
    def showPaneOfType_(self, pane_type: int):
        self.model.select_pane_of_type(pane_type)
    
    def closePaneAtIndex_(self, index: int):
        self.model.close_pane(index)
    
    def movePaneAtIndex_toIndex_(self, pane_index: int, dest_index: int):
        self.model.move_pane(pane_index, dest_index)
    
    def newTab(self):
        self.model.new_tab()
    
    def showAccount(self):
        self.model.show_account()
    
    def navigateBack(self):
        self.model.navigate_back()
    
    def jumpToAccount(self):
        self.model.jump_to_account()
    
    def toggleAreaVisibility_(self, area: int):
        self.model.toggle_area_visibility(area)
    
    #--- Item Management
    def deleteItem(self):
        self.model.delete_item()
    
    def duplicateItem(self):
        self.model.duplicate_item()
    
    def editItem(self):
        self.model.edit_item()
    
    def makeScheduleFromSelected(self):
        self.model.make_schedule_from_selected()
    
    def moveDown(self):
        self.model.move_down()
    
    def moveUp(self):
        self.model.move_up()
    
    def newItem(self):
        self.model.new_item()
    
    def newGroup(self):
        self.model.new_group()
    
    #--- Other
    def export(self):
        self.model.export()
    
    def statusLine(self) -> str:
        return self.model.status_line
    
    def hiddenAreas(self) -> list:
        return list(self.model.hidden_areas)
    
    #--- Column menu
    def columnMenuItems(self) -> list:
        return self.model.column_menu_items()
    
    def toggleColumnMenuItemAtIndex_(self, index: int):
        self.model.toggle_column_menu_item(index)
    
    #--- Python -> Cocoa
    @dontwrap
    def change_current_pane(self):
        self.callback.changeSelectedPane()
    
    @dontwrap
    def refresh_panes(self):
        self.callback.refreshPanes()
    
    @dontwrap
    def refresh_undo_actions(self):
        self.callback.refreshUndoActions()
    
    @dontwrap
    def show_custom_date_range_panel(self):
        self.callback.showCustomDateRangePanel()
    
    @dontwrap
    def refresh_status_line(self):
        self.callback.refreshStatusLine()
    
    @dontwrap
    def show_message(self, message):
        self.callback.showMessage_(message)
    
    @dontwrap
    def update_area_visibility(self):
        self.callback.updateAreaVisibility()
    
    @dontwrap
    def view_closed(self, index):
        self.callback.viewClosedAtIndex_(index)
    

class PyImportTable(PyTable):
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
    def setSwapButtonEnabled_(self, enabled: bool): pass
    def show(self): pass
    def updateSelectedPane(self): pass

class PyImportWindow(PyGUIObject):
    def __init__(self, document: pyref):
        model = ImportWindow(document.model)
        PyGUIObject.__init__(self, model)
    
    def importTable(self) -> pyref:
        return self.model.import_table
    
    def swapTypeList(self) -> pyref:
        return self.model.swap_type_list
    
    def accountCountAtIndex_(self, index: int) -> int:
        return self.model.panes[index].count
    
    def accountNameAtIndex_(self, index: int) -> str:
        return self.model.panes[index].name
    
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
    def set_swap_button_enabled(self, enabled):
        self.callback.setSwapButtonEnabled_(enabled)
    
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

class PyCSVImportOptions(PyGUIObject):
    def __init__(self, document: pyref):
        model = CSVOptions(document.model)
        PyGUIObject.__init__(self, model)
    
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
        self.date_format = clean_format(proxy.systemShortDateFormat())
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
    

class PyCompletableEdit(PyGUIObject):
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
        self.model = self.py_class(parent.model)
    
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
