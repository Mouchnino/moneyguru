/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGConst.h"
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
- (MGBaseView *)viewFromPaneType:(MGPaneType)paneType modelRef:(PyObject *)modelRef;

/* Actions */
- (void)columnMenuClick:(id)sender;
- (void)delete:(id)sender;
- (void)duplicateItem;
- (void)editItemInfo;
- (void)itemSegmentClicked:(id)sender;
- (void)jumpToAccount;
- (void)makeScheduleFromSelected;
- (void)moveSelectionDown;
- (void)moveSelectionUp;
- (void)navigateBack;
- (void)newGroup;
- (void)newItem;
- (void)newTab;
- (void)search;
- (void)selectMonthRange;
- (void)selectNextDateRange;
- (void)selectPrevDateRange;
- (void)selectTodayDateRange;
- (void)selectQuarterRange;
- (void)selectYearRange;
- (void)selectYearToDateRange;
- (void)selectRunningYearRange;
- (void)selectAllTransactionsRange;
- (void)selectCustomDateRange;
- (void)selectSavedCustomRange:(id)sender;
- (void)showBalanceSheet;
- (void)showIncomeStatement;
- (void)showTransactionTable;
- (void)showNextView;
- (void)showPreviousView;
- (void)showSelectedAccount;
- (void)toggleReconciliationMode;
- (void)toggleEntriesReconciled;
- (void)toggleExcluded;
- (void)toggleAreaVisibility:(id)sender;
- (void)toggleGraph;
- (void)togglePieChart;
- (void)export;

/* Public */

- (MGPrintView *)viewToPrint;
- (NSInteger)openedTabCount;
- (void)closeActiveTab;

/* Delegate */
- (BOOL)validateMenuItem:(NSMenuItem *)aItem;
- (BOOL)validateUserInterfaceItem:(id < NSValidatedUserInterfaceItem >)aItem;

@end
