/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

/* i18n */
// NSLocalizedString is way too long
#define TR(s) NSLocalizedString(s, @"")

/* Pasteboard types */

#define MGEntryPasteboardType @"MGEntryPasteboardType"
#define MGImportEntryPasteboardType @"MGImportEntryPasteboardType"
#define MGTransactionPasteboardType @"MGTransactionPasteboardType"
#define MGPathPasteboardType @"MGPathPasteboardType"

/* Toolbar identifiers */

#define MGDateRangeToolbarItemIdentifier @"MGDateRangeToolbarItemIdentifier"
#define MGMainToolbarIdentifier @"MGMainToolbarIdentifier"
#define MGSearchFieldToolbarItemIdentifier @"MGSearchFieldToolbarItemIdentifier"
#define MGBalanceSheetToolbarItemIdentifier @"MGBalanceSheetToolbarItemIdentifier"
#define MGIncomeStatementToolbarItemIdentifier @"MGIncomeStatementToolbarItemIdentifier"
#define MGTransactionsToolbarItemIdentifier @"MGTransactionsToolbarItemIdentifier"
#define MGSchedulesToolbarItemIdentifier @"MGSchedulesToolbarItemIdentifier"
#define MGBudgetToolbarItemIdentifier @"MGBudgetToolbarItemIdentifier"

/* Menu Item Tags */

#define MGNewItemMenuItem 1000
#define MGCloseWindowMenuItem 1001
#define MGCustomSavedRangeStart 2000

/* Errors */

#define MGErrorDomain @"com.hardcoded_software.moneyguru.ErrorDomain"
#define MGFileFormatErrorCode 1
#define MGDemoLimitErrorCode 2
#define MGUnknownErrorCode 3

/* Preferences */

// Visibility
#define BalanceSheetDeltaColumnVisible @"BalanceSheetDeltaColumnVisible"
#define BalanceSheetDeltaPercColumnVisible @"BalanceSheetDeltaPercColumnVisible"
#define BalanceSheetStartColumnVisible @"BalanceSheetStartColumnVisible"
#define BalanceSheetBudgetedColumnVisible @"BalanceSheetBudgetedColumnVisible"
#define BalanceSheetAccountNumberColumnVisible @"BalanceSheetAccountNumberColumnVisible"
#define NetWorthGraphVisible @"NetWorthGraphVisible"
#define AssetLiabilityPieChartVisible @"AssetLiabilityPieChartVisible"
#define IncomeStatementDeltaColumnVisible @"IncomeStatementDeltaColumnVisible"
#define IncomeStatementDeltaPercColumnVisible @"IncomeStatementDeltaPercColumnVisible"
#define IncomeStatementLastColumnVisible @"IncomeStatementLastColumnVisible"
#define IncomeStatementBudgetedColumnVisible @"IncomeStatementBudgetedColumnVisible"
#define IncomeStatementAccountNumberColumnVisible @"IncomeStatementAccountNumberColumnVisible"
#define ProfitGraphVisible @"ProfitGraphVisible"
#define IncomeExpensePieChartVisible @"IncomeExpensePieChartVisible"
#define TransactionDescriptionColumnVisible @"TransactionDescriptionColumnVisible"
#define TransactionPayeeColumnVisible @"TransactionPayeeColumnVisible"
#define TransactionChecknoColumnVisible @"TransactionChecknoColumnVisible"
#define AccountDescriptionColumnVisible @"AccountDescriptionColumnVisible"
#define AccountPayeeColumnVisible @"AccountPayeeColumnVisible"
#define AccountChecknoColumnVisible @"AccountChecknoColumnVisible"
#define AccountReconciliationDateColumnVisible @"AccountReconciliationDateColumnVisible"
#define AccountGraphVisible @"AccountGraphVisible"
#define ScheduleDescriptionColumnVisible @"ScheduleDescriptionColumnVisible"
#define SchedulePayeeColumnVisible @"SchedulePayeeColumnVisible"
#define ScheduleChecknoColumnVisible @"ScheduleChecknoColumnVisible"

// Others
#define ShowRecurrenceScopeDialog @"ShowRecurrenceScopeDialog"
#define TableFontSize @"TableFontSize"

// ScheduleScope **Synced with the core**
#define ScheduleScopeLocal 0
#define ScheduleScopeGlobal 1
#define ScheduleScopeCancel 2

// Synced with the core
#define MGPaneTypeNetWorth 0
#define MGPaneTypeProfit 1
#define MGPaneTypeTransaction 2
#define MGPaneTypeAccount 3
#define MGPaneTypeSchedule 4
#define MGPaneTypeBudget 5
#define MGPaneTypeEmpty 100
