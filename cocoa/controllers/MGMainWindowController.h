/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSWindowController.h"
#import "PSMTabBarControl.h"
#import "MGAccountProperties.h"
#import "MGTransactionInspector.h"
#import "MGMassEditionPanel.h"
#import "MGSchedulePanel.h"
#import "MGBudgetPanel.h"
#import "MGExportPanel.h"
#import "MGAccountView.h"
#import "MGNetWorthView.h"
#import "MGProfitView.h"
#import "MGTransactionView.h"
#import "MGScheduleView.h"
#import "MGBudgetView.h"
#import "MGCashculatorView.h"
#import "MGGeneralLedgerView.h"
#import "MGEmptyView.h"
#import "MGSearchField.h"
#import "MGImportWindow.h"
#import "MGCSVImportOptions.h"
#import "MGCustomDateRangePanel.h"
#import "MGAccountReassignPanel.h"
#import "MGAccountLookup.h"
#import "MGCompletionLookup.h"
#import "MGDateRangeSelector.h"
#import "MGViewOptions.h"
#import "MGBaseView.h"
#import "MGPrintView.h"
#import "PyMainWindow.h"

@interface MGMainWindowController : HSWindowController
{
    IBOutlet NSTabView *tabView;
    IBOutlet PSMTabBarControl *tabBar;
    IBOutlet NSTextField *statusLabel;
    
    MGNetWorthView *netWorthView;
    MGProfitView *profitView;
    MGTransactionView *transactionView;
    MGAccountView *accountView;
    MGScheduleView *scheduleView;
    MGBudgetView *budgetView;
    MGCashculatorView *cashculatorView;
    MGGeneralLedgerView *ledgerView;
    MGEmptyView *emptyView;
    MGAccountProperties *accountProperties;
    MGTransactionInspector *transactionPanel;
    MGMassEditionPanel *massEditionPanel;
    MGSchedulePanel *schedulePanel;
    MGBudgetPanel *budgetPanel;
    MGExportPanel *exportPanel;
    MGSearchField *searchField;
    MGImportWindow *importWindow;
    MGCSVImportOptions *csvOptionsWindow;
    MGCustomDateRangePanel *customDateRangePanel;
    MGAccountReassignPanel *accountReassignPanel;
    MGAccountLookup *accountLookup;
    MGCompletionLookup *completionLookup;
    MGDateRangeSelector *dateRangeSelector;
    MGViewOptions *viewOptions;
    MGBaseView *top;
    NSMutableArray *subviews;
}
- (id)initWithDocument:(MGDocument *)document;
- (PyMainWindow *)py;
- (MGDocument *)document;
/* Private */
- (BOOL)validateAction:(SEL)action;

/* Actions */
- (IBAction)delete:(id)sender;
- (IBAction)duplicateItem:(id)sender;
- (IBAction)editItemInfo:(id)sender;
- (IBAction)itemSegmentClicked:(id)sender;
- (IBAction)jumpToAccount:(id)sender;
- (IBAction)makeScheduleFromSelected:(id)sender;
- (IBAction)moveDown:(id)sender;
- (IBAction)moveUp:(id)sender;
- (IBAction)navigateBack:(id)sender;
- (IBAction)newGroup:(id)sender;
- (IBAction)newItem:(id)sender;
- (IBAction)newTab:(id)sender;
- (IBAction)search:(id)sender;
- (IBAction)selectMonthRange:(id)sender;
- (IBAction)selectNextDateRange:(id)sender;
- (IBAction)selectPrevDateRange:(id)sender;
- (IBAction)selectTodayDateRange:(id)sender;
- (IBAction)selectQuarterRange:(id)sender;
- (IBAction)selectYearRange:(id)sender;
- (IBAction)selectYearToDateRange:(id)sender;
- (IBAction)selectRunningYearRange:(id)sender;
- (IBAction)selectAllTransactionsRange:(id)sender;
- (IBAction)selectCustomDateRange:(id)sender;
- (IBAction)selectSavedCustomRange:(id)sender;
- (IBAction)showBalanceSheet:(id)sender;
- (IBAction)showIncomeStatement:(id)sender;
- (IBAction)showTransactionTable:(id)sender;
- (IBAction)showNextView:(id)sender;
- (IBAction)showPreviousView:(id)sender;
- (IBAction)showSelectedAccount:(id)sender;
- (IBAction)toggleReconciliationMode:(id)sender;
- (IBAction)toggleEntriesReconciled:(id)sender;
- (IBAction)toggleExcluded:(id)sender;
- (IBAction)toggleViewOptionsVisible:(id)sender;
- (IBAction)export:(id)sender;

/* Public */

- (void)restoreState;
- (void)saveState;
- (MGPrintView *)viewToPrint;
- (NSInteger)openedTabCount;
- (void)closeActiveTab;

/* Delegate */
- (BOOL)validateMenuItem:(NSMenuItem *)aItem;
- (BOOL)validateUserInterfaceItem:(id < NSValidatedUserInterfaceItem >)aItem;

@end
