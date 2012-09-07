/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PSMTabBarControl.h"
#import "MGAccountProperties.h"
#import "MGTransactionInspector.h"
#import "MGMassEditionPanel.h"
#import "MGSchedulePanel.h"
#import "MGBudgetPanel.h"
#import "MGExportPanel.h"
#import "MGSearchField.h"
#import "MGImportWindow.h"
#import "MGCSVImportOptions.h"
#import "MGCustomDateRangePanel.h"
#import "MGAccountReassignPanel.h"
#import "MGAccountLookup.h"
#import "MGCompletionLookup.h"
#import "MGDateRangeSelector.h"
#import "MGBaseView.h"
#import "MGPrintView.h"
#import "MGMainWindow.h"
#import "PyMainWindow.h"

@interface MGMainWindowController : NSWindowController <NSToolbarDelegate, NSWindowDelegate>
{
    NSTabView *tabView;
    PSMTabBarControl *tabBar;
    NSTextField *statusLabel;
    NSSegmentedControl *visibilitySegments;
    
    PyMainWindow *model;
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
    MGBaseView *top;
    NSMutableArray *subviews;
}

@property (readwrite, retain) NSTabView *tabView;
@property (readwrite, retain) PSMTabBarControl *tabBar;
@property (readwrite, retain) NSTextField *statusLabel;
@property (readwrite, retain) NSSegmentedControl *visibilitySegments;

- (id)initWithDocument:(PyDocument *)document;
- (PyMainWindow *)model;
/* Private */
- (BOOL)validateAction:(SEL)action;
- (MGBaseView *)viewFromPaneType:(NSInteger)paneType modelRef:(PyObject *)modelRef;

/* Actions */
- (void)columnMenuClick:(id)sender;
- (void)delete:(id)sender;
- (void)duplicateItem:(id)sender;
- (void)editItemInfo:(id)sender;
- (void)itemSegmentClicked:(id)sender;
- (void)jumpToAccount:(id)sender;
- (void)makeScheduleFromSelected:(id)sender;
- (void)moveSelectionDown:(id)sender;
- (void)moveSelectionUp:(id)sender;
- (void)navigateBack:(id)sender;
- (void)newGroup:(id)sender;
- (void)newItem:(id)sender;
- (void)newTab:(id)sender;
- (void)search:(id)sender;
- (void)selectMonthRange:(id)sender;
- (void)selectNextDateRange:(id)sender;
- (void)selectPrevDateRange:(id)sender;
- (void)selectTodayDateRange:(id)sender;
- (void)selectQuarterRange:(id)sender;
- (void)selectYearRange:(id)sender;
- (void)selectYearToDateRange:(id)sender;
- (void)selectRunningYearRange:(id)sender;
- (void)selectAllTransactionsRange:(id)sender;
- (void)selectCustomDateRange:(id)sender;
- (void)selectSavedCustomRange:(id)sender;
- (void)showBalanceSheet:(id)sender;
- (void)showIncomeStatement:(id)sender;
- (void)showTransactionTable:(id)sender;
- (void)showNextView:(id)sender;
- (void)showPreviousView:(id)sender;
- (void)showSelectedAccount:(id)sender;
- (void)toggleReconciliationMode:(id)sender;
- (void)toggleEntriesReconciled:(id)sender;
- (void)toggleExcluded:(id)sender;
- (void)toggleAreaVisibility:(id)sender;
- (void)toggleGraph:(id)sender;
- (void)togglePieChart:(id)sender;
- (void)export:(id)sender;

/* Public */

- (MGPrintView *)viewToPrint;
- (NSInteger)openedTabCount;
- (void)closeActiveTab;

/* Delegate */
- (BOOL)validateMenuItem:(NSMenuItem *)aItem;
- (BOOL)validateUserInterfaceItem:(id < NSValidatedUserInterfaceItem >)aItem;

@end
