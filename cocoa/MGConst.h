/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

/* Pasteboard types */

#define MGEntryPasteboardType @"MGEntryPasteboardType"
#define MGImportEntryPasteboardType @"MGImportEntryPasteboardType"
#define MGTransactionPasteboardType @"MGTransactionPasteboardType"
#define MGPathPasteboardType @"MGPathPasteboardType"

/* Toolbar identifiers */

#define MGDateRangeToolbarItemIdentifier @"MGDateRangeToolbarItemIdentifier"
#define MGMainToolbarIdentifier @"MGMainToolbarIdentifier"
#define MGReconcileToolbarItemIdentifier @"MGReconcileToolbarItemIdentifier"
#define MGSearchFieldToolbarItemIdentifier @"MGSearchFieldToolbarItemIdentifier"
#define MGBalanceSheetToolbarItemIdentifier @"MGBalanceSheetToolbarItemIdentifier"
#define MGIncomeStatementToolbarItemIdentifier @"MGIncomeStatementToolbarItemIdentifier"
#define MGTransactionsToolbarItemIdentifier @"MGTransactionsToolbarItemIdentifier"
#define MGEntriesToolbarItemIdentifier @"MGEntriesToolbarItemIdentifier"
#define MGSchedulesToolbarItemIdentifier @"MGSchedulesToolbarItemIdentifier"
#define MGBudgetToolbarItemIdentifier @"MGBudgetToolbarItemIdentifier"

/* Menu Item Tags */

#define MGNewItemMenuItem 1

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
#define NetWorthGraphVisible @"NetWorthGraphVisible"
#define AssetLiabilityPieChartVisible @"AssetLiabilityPieChartVisible"
#define IncomeStatementDeltaColumnVisible @"IncomeStatementDeltaColumnVisible"
#define IncomeStatementDeltaPercColumnVisible @"IncomeStatementDeltaPercColumnVisible"
#define IncomeStatementLastColumnVisible @"IncomeStatementLastColumnVisible"
#define IncomeStatementBudgetedColumnVisible @"IncomeStatementBudgetedColumnVisible"
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

/* Registration */

#define APPNAME @"moneyGuru"
#define LIMIT_DESC @"In the demo version, documents with more than 100 transactions cannot be saved."